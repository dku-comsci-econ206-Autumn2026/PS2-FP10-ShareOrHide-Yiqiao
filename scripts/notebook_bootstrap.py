"""Shared source for the first executable cell in generated notebooks."""

from textwrap import dedent


REPO_URL = (
    "https://github.com/dku-comsci-econ206-Autumn2026/"
    "PS2-FP10-ShareOrHide-Yiqiao.git"
)
REPO_NAME = "PS2-FP10-ShareOrHide-Yiqiao"


def notebook_bootstrap_source(
    repo_url: str = REPO_URL,
    repo_name: str = REPO_NAME,
    colab_base: str = "/content",
) -> str:
    """Return self-contained local/Colab repository bootstrap code.

    Arguments make the bootstrap independently testable with a local Git
    repository and a temporary Colab-like directory, without live networking.
    Generated notebooks always use the public defaults above.
    """

    return dedent(
        f"""
        from pathlib import Path
        import subprocess
        import sys

        REPO_URL = {repo_url!r}
        REPO_NAME = {repo_name!r}
        IN_COLAB = "google.colab" in sys.modules

        if IN_COLAB:
            ROOT = Path({colab_base!r}) / REPO_NAME
            if not ROOT.exists():
                subprocess.run(
                    ["git", "clone", "--depth", "1", REPO_URL, str(ROOT)],
                    check=True,
                )
        else:
            ROOT = Path.cwd().resolve()
            if ROOT.name == "notebooks":
                ROOT = ROOT.parent

        if not (ROOT / "src").is_dir():
            raise RuntimeError(
                f"Expected a repository containing src/ at {{ROOT}}. "
                "Run locally from the repository root or notebooks directory."
            )
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        """
    ).strip()


BOOTSTRAP_SOURCE = notebook_bootstrap_source()
