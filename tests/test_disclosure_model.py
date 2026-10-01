import unittest
from pathlib import Path

import numpy as np

from src.disclosure_model import (
    ACTIONS,
    CONFIDENTIALITY_COSTS,
    CONGESTION,
    DISCLOSURE_LEVELS,
    PRIVACY_COSTS,
    TYPE_PROB,
    TYPES,
    all_pure_strategies,
    coordination_benefit,
    expected_equilibrium_welfare,
    expected_first_best_welfare,
    expected_utility_action,
    find_pure_bne,
    first_best_for_types,
    privacy_cost,
    social_welfare,
    utility,
)


EXPECTED_BNE = {
    "Low": (("M", "M"), ("M", "M")),
    "Medium": (("P", "M"), ("P", "M")),
    "High": (("P", "P"), ("P", "P")),
}


class BaselineDisclosureModelTests(unittest.TestCase):
    def test_action_and_type_spaces(self):
        self.assertEqual(ACTIONS, ("M", "P", "F"))
        self.assertEqual(TYPES, ("L", "H"))
        self.assertEqual(DISCLOSURE_LEVELS, {"M": 0.0, "P": 1.0, "F": 2.0})
        self.assertEqual(PRIVACY_COSTS, {"M": 0.0, "P": 1.0, "F": 2.5})
        self.assertEqual(CONFIDENTIALITY_COSTS, {"L": 1.0, "H": 1.6})

    def test_type_probabilities_sum_to_one(self):
        self.assertAlmostEqual(sum(TYPE_PROB.values()), 1.0)
        self.assertTrue(all(probability >= 0 for probability in TYPE_PROB.values()))

    def test_minimum_has_zero_voluntary_privacy_cost(self):
        for confidentiality_type in TYPES:
            self.assertEqual(privacy_cost("M", confidentiality_type), 0.0)

    def test_coordination_benefit_weakly_increases_with_total_disclosure(self):
        ordered_profiles = [("M", "M"), ("M", "P"), ("P", "P"), ("P", "F"), ("F", "F")]
        benefits = [coordination_benefit(a, b, 0.6) for a, b in ordered_profiles]
        self.assertTrue(np.all(np.diff(benefits) >= -1e-12))

    def test_positive_disclosure_benefit_increases_with_congestion(self):
        benefits = [coordination_benefit("P", "P", d) for d in CONGESTION.values()]
        self.assertTrue(np.all(np.diff(benefits) > 0))

    def test_required_utility_value(self):
        self.assertAlmostEqual(utility("P", "P", "L", 1.0), 3.7409041912, places=9)

    def test_exactly_nine_bayesian_strategies(self):
        strategies = all_pure_strategies()
        self.assertEqual(len(strategies), 9)
        self.assertEqual(len(set(strategies)), 9)
        self.assertIn(("P", "M"), strategies)

    def test_expected_utility_check_against_p_m(self):
        expected = {
            "L": {"M": 0.885, "P": 1.308, "F": 0.670},
            "H": {"M": 0.885, "P": 0.708, "F": -0.830},
        }
        for own_type in TYPES:
            for action in ACTIONS:
                observed = expected_utility_action(action, own_type, ("P", "M"), 0.6)
                self.assertAlmostEqual(observed, expected[own_type][action], places=3)

    def test_equilibrium_finder_searches_all_profiles(self):
        for d in CONGESTION.values():
            self.assertEqual(find_pure_bne(d).profiles_checked, 81)

    def test_benchmark_bne(self):
        for label, d in CONGESTION.items():
            result = find_pure_bne(d)
            self.assertEqual(result.equilibria, (EXPECTED_BNE[label],))

    def test_expected_welfare_benchmarks(self):
        expected = {
            "Low": (0.0, 0.6390946522),
            "Medium": (2.1928832887, 3.1390850295),
            "High": (6.8818083824, 7.3852377939),
        }
        for label, d in CONGESTION.items():
            equilibrium = find_pure_bne(d).equilibria[0]
            bne = expected_equilibrium_welfare(equilibrium, d)
            first_best = expected_first_best_welfare(d)
            self.assertAlmostEqual(bne, expected[label][0], places=8)
            self.assertAlmostEqual(first_best, expected[label][1], places=8)

    def test_first_best_never_below_bne(self):
        for d in CONGESTION.values():
            first_best = expected_first_best_welfare(d)
            for equilibrium in find_pure_bne(d):
                self.assertGreaterEqual(
                    first_best + 1e-10,
                    expected_equilibrium_welfare(equilibrium, d),
                )

    def test_asymmetric_equilibria_are_supported(self):
        result = find_pure_bne(0.34)
        self.assertTrue(any(strategy_a != strategy_b for strategy_a, strategy_b in result))
        self.assertEqual(result.profiles_checked, 81)

    def test_first_best_ties_are_preserved(self):
        result = first_best_for_types("H", "H", CONGESTION["Low"])
        self.assertEqual(set(result.profiles), {("M", "P"), ("P", "M")})
        for profile in result.profiles:
            self.assertAlmostEqual(
                social_welfare(*profile, "H", "H", CONGESTION["Low"]),
                result.welfare,
            )

    def test_generated_outputs_exist(self):
        required = [
            "outputs/tables/baseline_bne_summary.csv",
            "outputs/tables/first_best_by_type.csv",
            "outputs/tables/baseline_welfare_gap.csv",
            "outputs/tables/ccar_alpha_sensitivity.csv",
            "outputs/tables/confidentiality_sensitivity.csv",
            "outputs/tables/full_disclosure_sensitivity.csv",
            "outputs/figures/baseline_welfare_comparison.png",
            "outputs/figures/baseline_welfare_gap.svg",
            "outputs/figures/confidentiality_equilibrium_phase.png",
        ]
        for relative_path in required:
            self.assertTrue(Path(relative_path).is_file(), relative_path)


class CCARTests(unittest.TestCase):
    def test_benchmark_ccar_bne(self):
        expected = {
            "Low": (("M", "M"), ("M", "M")),
            "Medium": (("P", "P"), ("P", "P")),
            "High": (("P", "P"), ("P", "P")),
        }
        for label, d in CONGESTION.items():
            result = find_pure_bne(d, ccar=True, alpha_m=0.7)
            self.assertEqual(result.equilibria, (expected[label],))

    def test_underlying_welfare_does_not_count_access_penalty(self):
        underlying = social_welfare(
            "M", "P", "L", "L", 0.6, accounting="underlying", ccar=True, alpha_m=0.5
        )
        baseline = social_welfare("M", "P", "L", "L", 0.6)
        operator = social_welfare(
            "M", "P", "L", "L", 0.6, accounting="operator", ccar=True, alpha_m=0.5
        )
        self.assertAlmostEqual(underlying, baseline)
        self.assertLess(operator, underlying)


if __name__ == "__main__":
    unittest.main()

