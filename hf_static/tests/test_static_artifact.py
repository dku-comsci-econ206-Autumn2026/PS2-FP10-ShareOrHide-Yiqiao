from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.export_static_model_data import ALPHA_M, build_export, state_key
from src.disclosure_model import (
    ACTIONS,
    CONGESTION,
    TYPES,
    expected_equilibrium_welfare,
    expected_first_best_welfare,
    find_pure_bne,
    first_best_for_types,
    strategy_to_mapping,
)


STATIC = ROOT / "hf_static"
DATA_PATH = STATIC / "data" / "validated_model_data.json"


class StaticArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exported = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.fresh = build_export()

    def test_exported_json_comes_from_validated_model_files(self):
        hashes = self.exported["metadata"]["source_file_hashes"]
        for relative_path, expected in hashes.items():
            actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected)
        self.assertEqual(
            self.exported["metadata"]["model_parameter_hash"],
            self.fresh["metadata"]["model_parameter_hash"],
        )

    def test_json_expected_bne_matches_root_model(self):
        for label, d in CONGESTION.items():
            for mechanism in ("baseline", "ccar"):
                kwargs = {"ccar": True, "alpha_m": ALPHA_M} if mechanism == "ccar" else {}
                result = find_pure_bne(d, **kwargs)
                self.assertEqual(len(result), 1)
                expected_a = strategy_to_mapping(result.equilibria[0][0])
                expected_b = strategy_to_mapping(result.equilibria[0][1])
                actual = self.exported["benchmarks"][mechanism][label]
                self.assertEqual(actual["strategy_A"], expected_a)
                self.assertEqual(actual["strategy_B"], expected_b)

    def test_json_welfare_values_match_root_model(self):
        for label, d in CONGESTION.items():
            first_best = expected_first_best_welfare(d)
            for mechanism in ("baseline", "ccar"):
                kwargs = {"ccar": True, "alpha_m": ALPHA_M} if mechanism == "ccar" else {}
                equilibrium = find_pure_bne(d, **kwargs).equilibria[0]
                expected = expected_equilibrium_welfare(
                    equilibrium, d, accounting="underlying", **kwargs
                )
                actual = self.exported["benchmarks"][mechanism][label]
                self.assertAlmostEqual(actual["expected_induced_underlying_welfare"], expected)
                self.assertAlmostEqual(actual["expected_first_best_welfare"], first_best)
                self.assertAlmostEqual(actual["welfare_gap"], first_best - expected)

    def test_every_disclosure_state_required_by_ui_exists(self):
        index = self.exported["state_index"]
        expected_keys = {
            state_key(mechanism, label, own_type, rival_type, own_action, rival_action)
            for mechanism, label, own_type, rival_type, own_action, rival_action in product(
                ("baseline", "ccar"), CONGESTION, TYPES, TYPES, ACTIONS, ACTIONS
            )
        }
        self.assertEqual(len(expected_keys), 216)
        self.assertEqual(set(index), expected_keys)
        self.assertEqual(self.exported["metadata"]["state_record_count"], 216)

    def test_first_best_ties_are_preserved_in_every_record(self):
        for mechanism, label, own_type, rival_type, own_action, rival_action in product(
            ("baseline", "ccar"), CONGESTION, TYPES, TYPES, ACTIONS, ACTIONS
        ):
            record = self.exported["state_index"][
                state_key(mechanism, label, own_type, rival_type, own_action, rival_action)
            ]
            expected = first_best_for_types(own_type, rival_type, CONGESTION[label])
            self.assertEqual(
                record["first_best_profiles"], [list(profile) for profile in expected.profiles]
            )

    def test_static_app_contains_required_evidence_boundary(self):
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        required = (
            "Participant choices are not a representative sample of drone operators, firms, "
            "or the public."
        )
        self.assertGreaterEqual(html.count(required), 2)
        self.assertIn("stylized normalized benchmarks", html)

    def test_no_pii_input_fields_exist(self):
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        input_tags = "\n".join(re.findall(r"<input\b[^>]*>", html + app, flags=re.I))
        for forbidden in ("name", "email", "student-id", "student_id", "phone", "address"):
            self.assertNotRegex(input_tags.lower(), rf"(?:id|name|type)=[\"'][^\"']*{forbidden}")

    def test_no_external_network_endpoints_exist(self):
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("XMLHttpRequest", app)
        self.assertNotIn("WebSocket", app)
        self.assertNotIn("sendBeacon", app)
        self.assertNotRegex(app, r"https?://")
        fetches = re.findall(r"fetch\(([^)]+)\)", app)
        self.assertEqual(len(fetches), 1)
        self.assertIn("./data/validated_model_data.json", fetches[0])

    def test_space_metadata_declares_static_sdk(self):
        readme = (STATIC / "README.md").read_text(encoding="utf-8")
        self.assertIn("sdk: static", readme)
        self.assertIn("app_file: index.html", readme)
        self.assertNotIn("hardware:", readme)

    def test_auction_scenarios_are_commercial_truthful_benchmarks(self):
        auction = self.exported["auction"]
        self.assertEqual(set(auction["excluded_operator_types"]), {"emergency", "public-safety"})
        self.assertGreater(len(auction["session_scenarios"]), 0)
        for scenario in auction["session_scenarios"]:
            self.assertEqual(scenario["setting"], "Truthful IPV benchmark")
            for bidder, bid in scenario["rival_bids"].items():
                self.assertEqual(bid, scenario["values"][bidder])


if __name__ == "__main__":
    unittest.main()
