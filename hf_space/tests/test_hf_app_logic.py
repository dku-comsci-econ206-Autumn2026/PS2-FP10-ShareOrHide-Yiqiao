import hashlib
from pathlib import Path
import unittest

from hf_space.app_logic import (
    ACTION_LABELS,
    BEHAVIORAL_DATA_SCHEMA,
    EVIDENCE_BOUNDARY,
    FORBIDDEN_PII_FIELDS,
    generate_auction_scenario,
    generate_peer_scenario,
    generate_solo_scenario,
    peer_private_view,
    peer_round_reveal,
    run_auction_outcome,
    solo_public_view,
    submit_auction_bid,
    submit_baseline_decision,
    submit_ccar_decision,
    submit_peer_choice,
)
from hf_space.src.disclosure_model import (
    ACTIONS,
    CONGESTION,
    TYPES,
    find_pure_bne,
    first_best_for_types,
    strategy_to_mapping,
    utility,
)


class HFSpaceBehavioralLogicTests(unittest.TestCase):
    def test_scenario_generation_uses_only_valid_states_and_types(self):
        for seed in range(100):
            scenario = generate_solo_scenario(seed)
            self.assertIn(scenario["congestion_label"], CONGESTION)
            self.assertEqual(
                scenario["congestion"], CONGESTION[scenario["congestion_label"]]
            )
            self.assertIn(scenario["participant_type"], TYPES)
            self.assertIn(scenario["rival_type"], TYPES)

    def test_scenario_seed_is_reproducible_and_new_state_is_clean(self):
        first = generate_solo_scenario(206)
        second = generate_solo_scenario(206)
        self.assertEqual(first, second)
        updated, _ = submit_baseline_decision(first, "Minimum disclosure")
        fresh = generate_solo_scenario(207)
        self.assertNotIn("baseline_reveal", fresh)
        self.assertEqual(fresh["phase"], "baseline_choice")
        self.assertNotEqual(updated["scenario_id"], fresh["scenario_id"])

    def test_rival_type_hidden_before_reveal(self):
        scenario = generate_solo_scenario(10)
        public = solo_public_view(scenario)
        self.assertNotIn("rival_type", public)
        self.assertEqual(
            public["rival_confidentiality_sensitivity"],
            "Unknown until after submission",
        )

    def test_valid_choices_map_to_validated_action_codes(self):
        for label, action in ACTION_LABELS.items():
            scenario = generate_solo_scenario(31)
            updated, reveal = submit_baseline_decision(scenario, label)
            self.assertEqual(reveal["participant_action"], action)
            self.assertEqual(updated["records"]["baseline_choice"], action)

    def test_baseline_benchmark_lookup_matches_validated_model(self):
        scenario = generate_solo_scenario(77)
        _, reveal = submit_baseline_decision(scenario, "Partial disclosure")
        equilibrium = find_pure_bne(scenario["congestion"]).equilibria[0]
        expected = strategy_to_mapping(equilibrium[0])[scenario["participant_type"]]
        self.assertEqual(reveal["participant_benchmark_action"], expected)

    def test_ccar_benchmark_lookup_matches_validated_model(self):
        scenario = generate_solo_scenario(91)
        baseline_state, _ = submit_baseline_decision(scenario, "Minimum disclosure")
        _, reveal = submit_ccar_decision(baseline_state, "Partial disclosure")
        equilibrium = find_pure_bne(
            scenario["congestion"], ccar=True, alpha_m=0.7
        ).equilibria[0]
        expected = strategy_to_mapping(equilibrium[0])[scenario["participant_type"]]
        self.assertEqual(reveal["participant_benchmark_action"], expected)

    def test_participant_payoff_delegates_to_model_function(self):
        scenario = generate_solo_scenario(109)
        _, reveal = submit_baseline_decision(scenario, "Full disclosure")
        expected = utility(
            "F",
            reveal["rival_action"],
            scenario["participant_type"],
            scenario["congestion"],
        )
        self.assertAlmostEqual(reveal["participant_payoff"], expected)
        self.assertAlmostEqual(reveal["alternative_payoffs"]["F"], expected)

    def test_first_best_lookup_delegates_to_model_function(self):
        scenario = generate_solo_scenario(110)
        _, reveal = submit_baseline_decision(scenario, "Partial disclosure")
        expected = first_best_for_types(
            scenario["participant_type"],
            scenario["rival_type"],
            scenario["congestion"],
        )
        self.assertEqual(reveal["first_best_profiles"], expected.profiles)
        self.assertAlmostEqual(reveal["first_best_welfare"], expected.welfare)

    def test_truthful_auction_benchmark(self):
        values = {"Participant": 8, "B": 5, "C": 3, "D": 2}
        outcome = run_auction_outcome(values, values)
        self.assertEqual(outcome["winner"], "Participant")
        self.assertEqual(outcome["payment"], 5)
        self.assertEqual(outcome["participant_utility"], 3)
        self.assertTrue(outcome["allocation_efficient"])

    def test_auction_scenario_and_submission_are_reproducible(self):
        first = generate_auction_scenario(206, "Noisy-bidding stress test")
        second = generate_auction_scenario(206, "Noisy-bidding stress test")
        self.assertEqual(first, second)
        _, first_outcome = submit_auction_bid(first, 5)
        _, second_outcome = submit_auction_bid(second, 5)
        self.assertEqual(first_outcome, second_outcome)

    def test_peer_transition_hides_player_a_before_player_b_submits(self):
        state = generate_peer_scenario(206)
        after_a = submit_peer_choice(state, "Partial disclosure", "privacy")
        self.assertEqual(after_a["phase"], "baseline_B")
        public_b = peer_private_view(after_a)
        self.assertEqual(public_b["role"], "Operator B")
        self.assertNotIn("A", public_b)
        self.assertNotIn("types", public_b)
        self.assertNotIn("choices", public_b)
        self.assertEqual(public_b["rival_type"], "Unknown")
        self.assertEqual(public_b["rival_action"], "Hidden until both submit")

    def test_peer_reveal_requires_both_submissions(self):
        state = generate_peer_scenario(19)
        after_a = submit_peer_choice(state, "Minimum disclosure")
        with self.assertRaises(ValueError):
            peer_round_reveal(after_a)
        after_b = submit_peer_choice(after_a, "Full disclosure")
        reveal = peer_round_reveal(after_b)
        self.assertEqual(set(reveal["types"]), {"A", "B"})
        self.assertEqual(set(reveal["choices"]), {"A", "B"})

    def test_emergency_public_safety_not_routed_as_commercial_bidder(self):
        values = {"Participant": 4, "Emergency": 100, "Public": 90, "B": 3}
        operator_types = {
            "Participant": "commercial",
            "Emergency": "emergency",
            "Public": "public-safety",
            "B": "commercial",
        }
        outcome = run_auction_outcome(values, values, operator_types)
        self.assertEqual(outcome["winner"], "Participant")
        self.assertEqual(set(outcome["excluded_operators"]), {"Emergency", "Public"})

    def test_behavioral_schema_has_no_pii_fields(self):
        self.assertTrue(BEHAVIORAL_DATA_SCHEMA.isdisjoint(FORBIDDEN_PII_FIELDS))
        self.assertNotIn("email", BEHAVIORAL_DATA_SCHEMA)
        self.assertNotIn("student_id", BEHAVIORAL_DATA_SCHEMA)

    def test_evidence_boundary_is_prominent_app_content(self):
        self.assertIn("exploratory classroom decision exercise", EVIDENCE_BOUNDARY)
        self.assertIn("not a representative sample", EVIDENCE_BOUNDARY)
        app_source = Path("hf_space/app.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(app_source.count("EVIDENCE_BOUNDARY"), 3)

    def test_no_external_api_or_secret_mechanism(self):
        source = "\n".join(
            Path(path).read_text(encoding="utf-8")
            for path in ("hf_space/app.py", "hf_space/app_logic.py")
        ).lower()
        for forbidden in ("openai", "api_key", "requests.post", "httpx.post"):
            self.assertNotIn(forbidden, source)

    def test_copied_models_match_validated_root_modules_byte_for_byte(self):
        for name in ("disclosure_model.py", "priority_slot_allocation.py"):
            root_bytes = Path("src", name).read_bytes()
            space_bytes = Path("hf_space", "src", name).read_bytes()
            self.assertEqual(hashlib.sha256(root_bytes).hexdigest(), hashlib.sha256(space_bytes).hexdigest())


if __name__ == "__main__":
    unittest.main()

