import unittest
from pathlib import Path

import numpy as np

from src.priority_slot_allocation import (
    allocate_fcfs,
    second_price_auction,
    simulate_bid_noise_stress,
    simulate_truthful_comparison,
)


VALUES = {"A": 8, "B": 5, "C": 3, "D": 2}


class PrioritySlotAllocationTests(unittest.TestCase):
    def test_fcfs_respects_request_order(self):
        result = allocate_fcfs(["B", "C", "A", "D"], VALUES, capacity=1)
        self.assertEqual(result.winners, ("B",))
        self.assertEqual(result.allocated_value, 5)
        self.assertAlmostEqual(result.allocative_efficiency, 5 / 8)

    def test_fcfs_stops_at_capacity(self):
        result = allocate_fcfs(["D", "B", "C", "A"], VALUES, capacity=2)
        self.assertEqual(result.winners, ("D", "B"))
        self.assertEqual(len(result.winners), 2)

    def test_second_price_selects_highest_bid_and_second_price(self):
        result = second_price_auction(
            {"A": 4, "B": 9, "C": 6}, {"A": 8, "B": 5, "C": 3}
        )
        self.assertEqual(result.winner, "B")
        self.assertEqual(result.payment, 6)

    def test_truthful_benchmark(self):
        result = second_price_auction(VALUES)
        self.assertEqual(result.winner, "A")
        self.assertEqual(result.payment, 5)
        self.assertEqual(result.winner_utility, 8 - 5)

    def test_payments_nonnegative_and_efficiency_in_range(self):
        fcfs = allocate_fcfs(["B", "C", "A", "D"], VALUES)
        auction = second_price_auction(VALUES)
        for result in (fcfs, auction):
            self.assertGreaterEqual(result.payment, 0)
            self.assertGreaterEqual(result.allocative_efficiency, 0)
            self.assertLessEqual(result.allocative_efficiency, 1)

    def test_simulation_efficiencies_in_range(self):
        simulation = simulate_truthful_comparison(rounds=500, seed=91)
        for key in ("fcfs_efficiency", "second_price_efficiency"):
            self.assertTrue(np.all(simulation[key] >= 0))
            self.assertTrue(np.all(simulation[key] <= 1))

    def test_simulation_reproducible_with_fixed_seed(self):
        first = simulate_truthful_comparison(rounds=200, seed=206)
        second = simulate_truthful_comparison(rounds=200, seed=206)
        for key in first:
            np.testing.assert_array_equal(first[key], second[key])
        self.assertEqual(
            simulate_bid_noise_stress(rounds=200, seed=1206),
            simulate_bid_noise_stress(rounds=200, seed=1206),
        )

    def test_emergency_and_public_safety_are_explicitly_excluded(self):
        values = {"commercial": 2, "emergency": 100, "public": 90}
        types = {
            "commercial": "commercial",
            "emergency": "emergency",
            "public": "public-safety",
        }
        fcfs = allocate_fcfs(
            ["emergency", "public", "commercial"], values, operator_types=types
        )
        auction = second_price_auction(values, operator_types=types)
        self.assertEqual(fcfs.winners, ("commercial",))
        self.assertEqual(auction.winner, "commercial")
        self.assertEqual(fcfs.excluded_operators, ("emergency", "public"))
        self.assertEqual(auction.excluded_operators, ("emergency", "public"))

    def test_simulation_summary_is_computed_not_hard_coded(self):
        short = simulate_truthful_comparison(rounds=100, seed=1)
        long = simulate_truthful_comparison(rounds=101, seed=1)
        self.assertEqual(short["fcfs_efficiency"].shape, (100,))
        self.assertEqual(long["fcfs_efficiency"].shape, (101,))
        self.assertNotEqual(
            float(np.mean(short["fcfs_efficiency"])),
            float(np.mean(long["fcfs_efficiency"])),
        )

    def test_required_notebook_uses_simulation_functions(self):
        notebook = Path("notebooks/02_priority_slot_allocation.ipynb").read_text()
        self.assertIn("simulate_truthful_comparison", notebook)
        self.assertIn("simulate_bid_noise_stress", notebook)


if __name__ == "__main__":
    unittest.main()
