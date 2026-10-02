from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import nbformat

from scripts.notebook_bootstrap import (
    BOOTSTRAP_SOURCE,
    REPO_NAME,
    REPO_URL,
    notebook_bootstrap_source,
)


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = (
    ROOT / "notebooks" / "01_strategic_disclosure_game.ipynb",
    ROOT / "notebooks" / "02_priority_slot_allocation.ipynb",
)
GENERATORS = (
    ROOT / "scripts" / "build_disclosure_notebook.py",
    ROOT / "scripts" / "build_priority_slot_notebook.py",
)


def first_code_cell(path: Path) -> str:
    notebook = nbformat.read(path, as_version=4)
    return next(cell.source for cell in notebook.cells if cell.cell_type == "code")


class NotebookPortabilityTests(unittest.TestCase):
    def test_generated_notebooks_share_the_canonical_bootstrap(self):
        for path in NOTEBOOKS:
            with self.subTest(path=path.name):
                source = first_code_cell(path)
                self.assertTrue(source.startswith(BOOTSTRAP_SOURCE))
                self.assertIn(f"REPO_URL = {REPO_URL!r}", source)
                self.assertIn(f"REPO_NAME = {REPO_NAME!r}", source)
                self.assertIn('IN_COLAB = "google.colab" in sys.modules', source)

    def test_path_is_imported_before_it_is_used(self):
        for path in NOTEBOOKS:
            with self.subTest(path=path.name):
                source = first_code_cell(path)
                self.assertLess(
                    source.index("from pathlib import Path"),
                    source.index("Path.cwd()"),
                )

    def test_generators_use_the_shared_bootstrap(self):
        for path in GENERATORS:
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn("from notebook_bootstrap import BOOTSTRAP_SOURCE", source)
                self.assertIn("BOOTSTRAP_SOURCE", source)

    def test_no_user_specific_absolute_path_is_embedded(self):
        for path in (*NOTEBOOKS, *GENERATORS, ROOT / "scripts" / "notebook_bootstrap.py"):
            with self.subTest(path=path.name):
                self.assertNotIn(str(Path.home()), path.read_text(encoding="utf-8"))

    def test_bootstrap_imports_models_from_root_and_notebooks_directory(self):
        driver = textwrap.dedent(
            f"""
            namespace = {{}}
            exec({BOOTSTRAP_SOURCE!r}, namespace)
            from src.disclosure_model import find_pure_bne
            from src.priority_slot_allocation import second_price_auction
            assert namespace["ROOT"].name == {ROOT.name!r}
            assert find_pure_bne(1.0).equilibria
            assert second_price_auction({{"A": 8, "B": 5}}).winner == "A"
            """
        )
        for cwd in (ROOT, ROOT / "notebooks"):
            with self.subTest(cwd=cwd.name):
                result = subprocess.run(
                    [sys.executable, "-I", "-c", driver],
                    cwd=cwd,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_colab_like_bootstrap_clones_once_and_imports_models(self):
        cache = ROOT / ".pytest_cache"
        cache.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as temporary:
            temporary_path = Path(temporary)
            colab_base = temporary_path / "content"
            colab_base.mkdir()
            source = notebook_bootstrap_source(
                repo_url=ROOT.as_uri(),
                repo_name=REPO_NAME,
                colab_base=str(colab_base),
            )
            driver = textwrap.dedent(
                f"""
                import sys
                import types

                assert "src" not in sys.modules
                sys.modules["google.colab"] = types.ModuleType("google.colab")
                first = {{}}
                exec({source!r}, first)
                clone = first["ROOT"]
                sentinel = clone / ".bootstrap-reuse-check"
                sentinel.write_text("reuse", encoding="utf-8")

                second = {{}}
                exec({source!r}, second)
                assert second["ROOT"] == clone
                assert sentinel.read_text(encoding="utf-8") == "reuse"

                from src.disclosure_model import find_pure_bne
                from src.priority_slot_allocation import second_price_auction
                assert find_pure_bne(1.0).equilibria
                assert second_price_auction({{"A": 8, "B": 5}}).winner == "A"
                """
            )
            result = subprocess.run(
                [sys.executable, "-I", "-c", driver],
                cwd=temporary_path,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
