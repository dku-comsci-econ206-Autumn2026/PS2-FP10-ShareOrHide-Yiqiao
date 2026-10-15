import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "outputs" / "final"


class FinalReleaseEvidenceTests(unittest.TestCase):
    def test_required_final_evidence_files_exist(self):
        required = [
            "benchmark_results.csv",
            "robustness_results.csv",
            "belief_sensitivity.csv",
            "tolerance_sensitivity.csv",
            "experiment_manifest.json",
            "figure_metadata.json",
            "release_manifest.json",
        ]
        for name in required:
            self.assertTrue((FINAL / name).is_file(), name)

    def test_release_manifest_benchmark_values(self):
        data = json.loads((FINAL / "release_manifest.json").read_text())
        baseline = {
            row["Congestion"]: row
            for row in data["benchmark_rows"]
            if row["Mechanism"] == "Baseline"
        }
        self.assertAlmostEqual(baseline["Low"]["Welfare gap"], 0.6390946521519896)
        self.assertAlmostEqual(baseline["Medium"]["Welfare gap"], 0.9462017407996144)
        self.assertAlmostEqual(baseline["High"]["Welfare gap"], 0.5034294115088898)
        self.assertTrue(data["robustness_categories_overlap"])

    def test_robustness_grid_and_counts(self):
        with (FINAL / "robustness_results.csv").open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 760)
        fields = {
            "No effect on equilibrium set": 401,
            "Robust welfare improvement": 334,
            "Excessive disclosure by stated diagnostic": 18,
            "Any CCAR gap exceeds worst baseline gap": 3,
            "Multiple CCAR pure BNE": 66,
            "No CCAR pure BNE": 0,
        }
        for field, expected in fields.items():
            self.assertEqual(sum(row[field] == "True" for row in rows), expected, field)

    def test_tolerance_sensitivity_is_stable(self):
        with (FINAL / "tolerance_sensitivity.csv").open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 24)
        groups = {}
        for row in rows:
            key = (row["Congestion"], row["Mechanism"])
            groups.setdefault(key, set()).add(row["Pure BNE set"])
            self.assertEqual(int(row["Profiles checked"]), 81)
        self.assertTrue(all(len(outcomes) == 1 for outcomes in groups.values()))

    def test_belief_grid_probabilities_are_valid(self):
        with (FINAL / "belief_sensitivity.csv").open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 54)
        for row in rows:
            self.assertAlmostEqual(float(row["p_L"]) + float(row["p_H"]), 1.0)
            self.assertGreaterEqual(int(row["Pure BNE count"]), 1)


if __name__ == "__main__":
    unittest.main()
