"""Pure, session-local logic for the behavioral-science classroom artifact.

This module contains no UI framework code, persistence, network calls, accounts,
or external APIs. Economic outcomes delegate to the validated copied modules in
``hf_space/src``.
"""

from __future__ import annotations

from copy import deepcopy
from html import escape
import random
import secrets
from typing import Mapping, Sequence

try:  # Package import when tested from the repository root.
    from .src.disclosure_model import (
        ACTIONS,
        CONGESTION,
        DISCLOSURE_LEVELS,
        TYPES,
        equilibrium_label,
        expected_equilibrium_welfare,
        expected_first_best_welfare,
        find_pure_bne,
        first_best_for_types,
        social_welfare,
        strategy_to_mapping,
        utility,
    )
    from .src.priority_slot_allocation import (
        second_price_auction,
        simulate_truthful_comparison,
    )
except ImportError:  # Direct execution from inside hf_space/.
    from src.disclosure_model import (
        ACTIONS,
        CONGESTION,
        DISCLOSURE_LEVELS,
        TYPES,
        equilibrium_label,
        expected_equilibrium_welfare,
        expected_first_best_welfare,
        find_pure_bne,
        first_best_for_types,
        social_welfare,
        strategy_to_mapping,
        utility,
    )
    from src.priority_slot_allocation import (
        second_price_auction,
        simulate_truthful_comparison,
    )


ALPHA_M = 0.7
ACTION_LABELS = {
    "Minimum disclosure": "M",
    "Partial disclosure": "P",
    "Full disclosure": "F",
}
ACTION_NAMES = {code: label for label, code in ACTION_LABELS.items()}
TYPE_NAMES = {
    "L": "Low confidentiality sensitivity",
    "H": "High confidentiality sensitivity",
}
MOTIVATION_OPTIONS = (
    "Commercial privacy",
    "Traffic efficiency",
    "Expected payoff",
    "Reciprocity",
    "Fairness",
    "Competitive advantage",
    "Uncertainty about the rival",
    "Other",
)
EVIDENCE_BOUNDARY = (
    "**Evidence boundary:** This Space is an exploratory classroom decision exercise. "
    "Participant choices are not a representative sample of drone operators, firms, "
    "or the public. They do not establish how real operators would behave, and they "
    "do not validate the model's external accuracy.\n\n"
    "The numerical parameters are stylized normalized benchmarks rather than "
    "empirically calibrated estimates."
)

# Session-only fields. Reflections can contain whatever a participant types, but
# they are never persisted, exported automatically, or sent to an external API.
BEHAVIORAL_DATA_SCHEMA = frozenset(
    {
        "scenario_id",
        "congestion",
        "participant_type",
        "rival_type",
        "baseline_choice",
        "baseline_motivations",
        "baseline_reflection",
        "ccar_choice",
        "ccar_motivations",
        "ccar_reflection",
        "auction_value",
        "auction_bid",
        "auction_setting",
    }
)
FORBIDDEN_PII_FIELDS = frozenset(
    {"name", "email", "student_id", "login", "ip", "ip_address", "phone", "address"}
)


def _seed_value(seed: int | float | str | None) -> int:
    """Return a reproducible integer seed, or a secure random seed when blank."""
    if seed is None or seed == "":
        return secrets.randbits(63)
    try:
        return int(float(seed))
    except (TypeError, ValueError) as exc:
        raise ValueError("Demo seed must be an integer or left blank") from exc


def _action_code(choice: str) -> str:
    if choice in ACTION_LABELS:
        return ACTION_LABELS[choice]
    if choice in ACTIONS:
        return choice
    raise ValueError(f"Choose one of: {', '.join(ACTION_LABELS)}")


def _action_name(action: str) -> str:
    if action not in ACTION_NAMES:
        raise ValueError(f"Unknown action: {action}")
    return ACTION_NAMES[action]


def _benchmark(congestion: float, *, ccar: bool = False):
    kwargs = {"ccar": True, "alpha_m": ALPHA_M} if ccar else {}
    result = find_pure_bne(congestion, **kwargs)
    if len(result) != 1:
        raise RuntimeError("Validated benchmark state should have one pure BNE")
    return result.equilibria[0]


def strategy_explanation(strategy: Sequence[str]) -> str:
    """Describe a type-contingent strategy without an ambiguous bare tuple."""
    mapping = strategy_to_mapping(tuple(strategy))
    return (
        f"Low-confidentiality type → {_action_name(mapping['L'])}; "
        f"High-confidentiality type → {_action_name(mapping['H'])}"
    )


def generate_solo_scenario(seed: int | float | str | None = None) -> dict:
    """Create one reproducible internal scenario with a hidden rival type."""
    used_seed = _seed_value(seed)
    rng = random.Random(used_seed)
    congestion_label = rng.choice(tuple(CONGESTION))
    participant_type = rng.choice(TYPES)
    rival_type = rng.choice(TYPES)
    return {
        "mode": "solo",
        "phase": "baseline_choice",
        "scenario_id": f"solo-{used_seed}",
        "seed": used_seed,
        "congestion_label": congestion_label,
        "congestion": CONGESTION[congestion_label],
        "participant_type": participant_type,
        "rival_type": rival_type,
        "records": {},
    }


def solo_public_view(state: Mapping) -> dict:
    """Return exactly the information visible before the baseline submission."""
    if state.get("mode") != "solo":
        raise ValueError("Start a solo scenario first")
    return {
        "scenario_id": state["scenario_id"],
        "congestion": state["congestion_label"],
        "congestion_d": state["congestion"],
        "your_confidentiality_sensitivity": TYPE_NAMES[state["participant_type"]],
        "rival_confidentiality_sensitivity": "Unknown until after submission",
        "prior_rival_low": 0.5,
        "prior_rival_high": 0.5,
    }


def format_solo_scenario(state: Mapping) -> str:
    public = solo_public_view(state)
    return (
        "### Your private scenario\n"
        f"- **Current congestion:** {public['congestion']} (`d = {public['congestion_d']}`)\n"
        f"- **Your type:** {public['your_confidentiality_sensitivity']}\n"
        "- **Rival type:** unknown\n"
        "- **Prior:** 50% Low type, 50% High type\n\n"
        "Choose before seeing the rival or benchmark."
    )


def submit_baseline_decision(
    state: Mapping,
    choice: str,
    motivations: Sequence[str] | None = None,
    reflection: str = "",
) -> tuple[dict, dict]:
    """Record a choice and compute the baseline reveal from validated functions."""
    if not state or state.get("phase") != "baseline_choice":
        raise ValueError("Generate a new scenario before submitting a baseline choice")
    action = _action_code(choice)
    updated = deepcopy(dict(state))
    d = updated["congestion"]
    equilibrium = _benchmark(d)
    participant_strategy, rival_strategy = map(strategy_to_mapping, equilibrium)
    rival_action = rival_strategy[updated["rival_type"]]
    alternative_payoffs = {
        candidate: utility(
            candidate,
            rival_action,
            updated["participant_type"],
            d,
        )
        for candidate in ACTIONS
    }
    realized_welfare = social_welfare(
        action,
        rival_action,
        updated["participant_type"],
        updated["rival_type"],
        d,
    )
    first_best = first_best_for_types(
        updated["participant_type"], updated["rival_type"], d
    )
    reveal = {
        "rival_type": updated["rival_type"],
        "rival_action": rival_action,
        "participant_action": action,
        "participant_payoff": alternative_payoffs[action],
        "alternative_payoffs": alternative_payoffs,
        "participant_benchmark_action": participant_strategy[updated["participant_type"]],
        "benchmark_strategy_A": equilibrium[0],
        "benchmark_strategy_B": equilibrium[1],
        "realized_social_welfare": realized_welfare,
        "first_best_profiles": first_best.profiles,
        "first_best_welfare": first_best.welfare,
        "welfare_gap": first_best.welfare - realized_welfare,
    }
    updated["phase"] = "ccar_choice"
    updated["baseline_reveal"] = reveal
    updated["records"]["baseline_choice"] = action
    updated["records"]["baseline_motivations"] = tuple(motivations or ())
    updated["records"]["baseline_reflection"] = str(reflection or "")
    return updated, reveal


def format_payoff_table(payoffs: Mapping[str, float]) -> str:
    lines = ["| Your action | Your payoff |", "|---|---:|"]
    for action in ACTIONS:
        lines.append(f"| {_action_name(action)} | {payoffs[action]:.3f} |")
    return "\n".join(lines)


def format_baseline_reveal(state: Mapping, reveal: Mapping) -> str:
    first_best_text = ", ".join(
        f"A {_action_name(a)} / B {_action_name(b)}"
        for a, b in reveal["first_best_profiles"]
    )
    return (
        "### Baseline reveal\n"
        f"- **Rival realized type:** {TYPE_NAMES[reveal['rival_type']]}\n"
        f"- **Rival benchmark action:** {_action_name(reveal['rival_action'])}\n"
        f"- **Your choice:** {_action_name(reveal['participant_action'])}\n"
        f"- **Your realized payoff:** {reveal['participant_payoff']:.3f}\n\n"
        f"{format_payoff_table(reveal['alternative_payoffs'])}\n\n"
        "**Bayesian benchmark for this congestion state**  \n"
        f"{strategy_explanation(reveal['benchmark_strategy_A'])}.  \n"
        f"For your realized type: **{_action_name(reveal['participant_benchmark_action'])}**.\n\n"
        f"- **Realized social welfare:** {reveal['realized_social_welfare']:.3f}\n"
        f"- **Full-information first best:** {first_best_text}\n"
        f"- **First-best welfare:** {reveal['first_best_welfare']:.3f}\n"
        f"- **Realized welfare gap:** {reveal['welfare_gap']:.3f}\n\n"
        f"{EVIDENCE_BOUNDARY}"
    )


def submit_ccar_decision(
    state: Mapping,
    choice: str,
    motivations: Sequence[str] | None = None,
    reflection: str = "",
) -> tuple[dict, dict]:
    """Compute CCAR payoffs and underlying welfare using validated accounting."""
    if not state or state.get("phase") != "ccar_choice":
        raise ValueError("Submit the baseline round before the CCAR round")
    action = _action_code(choice)
    updated = deepcopy(dict(state))
    d = updated["congestion"]
    equilibrium = _benchmark(d, ccar=True)
    participant_strategy, rival_strategy = map(strategy_to_mapping, equilibrium)
    rival_action = rival_strategy[updated["rival_type"]]
    alternative_payoffs = {
        candidate: utility(
            candidate,
            rival_action,
            updated["participant_type"],
            d,
            ccar=True,
            alpha_m=ALPHA_M,
        )
        for candidate in ACTIONS
    }
    underlying_welfare = social_welfare(
        action,
        rival_action,
        updated["participant_type"],
        updated["rival_type"],
        d,
        accounting="underlying",
        ccar=True,
        alpha_m=ALPHA_M,
    )
    baseline_action = updated["records"]["baseline_choice"]
    direction = {
        -1: "decreased",
        0: "stayed the same",
        1: "increased",
    }[
        (DISCLOSURE_LEVELS[action] > DISCLOSURE_LEVELS[baseline_action])
        - (DISCLOSURE_LEVELS[action] < DISCLOSURE_LEVELS[baseline_action])
    ]
    reveal = {
        "rival_action": rival_action,
        "participant_action": action,
        "participant_payoff": alternative_payoffs[action],
        "alternative_payoffs": alternative_payoffs,
        "participant_benchmark_action": participant_strategy[updated["participant_type"]],
        "benchmark_strategy_A": equilibrium[0],
        "benchmark_strategy_B": equilibrium[1],
        "underlying_social_welfare": underlying_welfare,
        "baseline_action": baseline_action,
        "disclosure_change": direction,
        "baseline_benchmark": updated["baseline_reveal"]["participant_benchmark_action"],
    }
    updated["phase"] = "complete"
    updated["ccar_reveal"] = reveal
    updated["records"]["ccar_choice"] = action
    updated["records"]["ccar_motivations"] = tuple(motivations or ())
    updated["records"]["ccar_reflection"] = str(reflection or "")
    return updated, reveal


def format_ccar_reveal(state: Mapping, reveal: Mapping) -> str:
    return (
        "### CCAR comparison\n"
        f"- **Your baseline choice:** {_action_name(reveal['baseline_action'])}\n"
        f"- **Your CCAR choice:** {_action_name(reveal['participant_action'])}\n"
        f"- **Disclosure {reveal['disclosure_change']}**\n"
        f"- **Your CCAR payoff:** {reveal['participant_payoff']:.3f}\n\n"
        f"{format_payoff_table(reveal['alternative_payoffs'])}\n\n"
        f"- **Baseline theoretical benchmark for your type:** {_action_name(reveal['baseline_benchmark'])}\n"
        f"- **CCAR theoretical benchmark for your type:** {_action_name(reveal['participant_benchmark_action'])}\n"
        f"- **Underlying social welfare:** {reveal['underlying_social_welfare']:.3f}\n\n"
        "In the benchmark model, CCAR changes incentives in some parameter regions but not all. "
        "Sensitivity analysis also finds no-change, welfare-improvement, excessive-disclosure, "
        "increased-gap, and multiple-equilibrium regions.\n\n"
        f"{EVIDENCE_BOUNDARY}"
    )


def generate_auction_scenario(
    seed: int | float | str | None = None,
    setting: str = "Truthful benchmark",
) -> dict:
    """Create one commercial-only priority-slot scenario."""
    if setting not in {"Truthful benchmark", "Noisy-bidding stress test"}:
        raise ValueError("Unknown auction setting")
    used_seed = _seed_value(seed)
    rng = random.Random(used_seed)
    values = {"Participant": float(rng.randint(1, 10))}
    values.update({name: float(rng.randint(1, 10)) for name in ("B", "C", "D")})
    return {
        "phase": "bid",
        "seed": used_seed,
        "setting": setting,
        "values": values,
        "operator_types": {name: "commercial" for name in values},
    }


def run_auction_outcome(
    values: Mapping[str, float],
    bids: Mapping[str, float],
    operator_types: Mapping[str, str] | None = None,
) -> dict:
    """Delegate allocation and exclusions to the validated auction module."""
    result = second_price_auction(bids, values=values, operator_types=operator_types)
    eligible = [name for name in values if name not in result.excluded_operators]
    efficient_winner = sorted(eligible, key=lambda name: (-values[name], name))[0]
    return {
        "winner": result.winner,
        "payment": result.payment,
        "auctioneer_revenue": result.auctioneer_revenue,
        "participant_utility": (
            values["Participant"] - result.payment if result.winner == "Participant" else 0.0
        ),
        "efficient_winner": efficient_winner,
        "allocation_efficient": result.winner == efficient_winner,
        "excluded_operators": result.excluded_operators,
        "bids": dict(bids),
        "values": dict(values),
    }


def submit_auction_bid(state: Mapping, bid: float) -> tuple[dict, dict]:
    if not state or state.get("phase") != "bid":
        raise ValueError("Generate an auction scenario first")
    if bid is None or float(bid) < 0:
        raise ValueError("Bid must be a nonnegative normalized value")
    updated = deepcopy(dict(state))
    rng = random.Random(updated["seed"] + 7919)
    bids = {"Participant": float(bid)}
    for rival in ("B", "C", "D"):
        value = updated["values"][rival]
        if updated["setting"] == "Truthful benchmark":
            bids[rival] = value
        else:
            sigma = 0.5
            epsilon = rng.lognormvariate(-(sigma**2) / 2, sigma)
            bids[rival] = max(0.0, value * epsilon)
    outcome = run_auction_outcome(
        updated["values"], bids, updated["operator_types"]
    )
    outcome["setting"] = updated["setting"]
    updated["phase"] = "complete"
    updated["outcome"] = outcome
    return updated, outcome


def format_auction_outcome(outcome: Mapping) -> str:
    rows = ["| Operator | Private value | Bid |", "|---|---:|---:|"]
    for name in sorted(outcome["values"]):
        rows.append(
            f"| {name} | {outcome['values'][name]:.2f} | {outcome['bids'][name]:.2f} |"
        )
    setting_note = (
        "Rival bids equal values in the truthful IPV benchmark."
        if outcome["setting"] == "Truthful benchmark"
        else "Rival bids include multiplicative noise. This is a non-equilibrium behavioral stress test."
    )
    return (
        "### Priority-slot result\n"
        + "\n".join(rows)
        + "\n\n"
        + f"- **Winner:** {outcome['winner']}\n"
        + f"- **Second-highest payment:** {outcome['payment']:.2f}\n"
        + f"- **Your utility:** {outcome['participant_utility']:.2f}\n"
        + f"- **Efficient winner by private value:** {outcome['efficient_winner']}\n"
        + f"- **Efficient allocation:** {'Yes' if outcome['allocation_efficient'] else 'No'}\n\n"
        + setting_note
        + "\n\nUnder the standard IPV second-price benchmark, bidding your true value is weakly "
        "dominant. This statement does not extend to common- or interdependent-value settings."
    )


def generate_peer_scenario(seed: int | float | str | None = None) -> dict:
    """Assign two private types and a common public congestion state."""
    used_seed = _seed_value(seed)
    rng = random.Random(used_seed)
    congestion_label = rng.choice(tuple(CONGESTION))
    return {
        "mode": "peer",
        "seed": used_seed,
        "phase": "baseline_A",
        "congestion_label": congestion_label,
        "congestion": CONGESTION[congestion_label],
        "types": {"A": rng.choice(TYPES), "B": rng.choice(TYPES)},
        "baseline_choices": {},
        "ccar_choices": {},
        "reflections": {},
    }


def peer_private_view(state: Mapping) -> dict:
    """Return only the current player's information; never leak the prior player."""
    phase = state.get("phase", "") if state else ""
    if phase not in {"baseline_A", "baseline_B", "ccar_A", "ccar_B"}:
        raise ValueError("Start or advance peer play to a private decision turn")
    player = phase[-1]
    mechanism = "Baseline" if phase.startswith("baseline") else "CCAR"
    return {
        "role": f"Operator {player}",
        "mechanism": mechanism,
        "congestion": state["congestion_label"],
        "congestion_d": state["congestion"],
        "your_confidentiality_sensitivity": TYPE_NAMES[state["types"][player]],
        "rival_type": "Unknown",
        "rival_action": "Hidden until both submit",
    }


def format_peer_private_view(state: Mapping) -> str:
    view = peer_private_view(state)
    return (
        f"### {view['role']} — {view['mechanism']} round\n"
        f"- **Congestion:** {view['congestion']} (`d = {view['congestion_d']}`)\n"
        f"- **Your private type:** {view['your_confidentiality_sensitivity']}\n"
        "- **Other operator:** type and action hidden\n\n"
        "Make your choice, then pass the screen when prompted."
    )


def submit_peer_choice(
    state: Mapping,
    choice: str,
    motivation: str = "",
) -> dict:
    """Advance the pass-the-screen state machine without exposing prior choices."""
    if not state:
        raise ValueError("Start peer play first")
    phase = state.get("phase", "")
    if phase not in {"baseline_A", "baseline_B", "ccar_A", "ccar_B"}:
        raise ValueError("No peer decision is currently expected")
    updated = deepcopy(dict(state))
    action = _action_code(choice)
    mechanism, player = phase.split("_")
    updated[f"{mechanism}_choices"][player] = action
    updated["reflections"][f"{mechanism}_{player}"] = str(motivation or "")
    if player == "A":
        updated["phase"] = f"{mechanism}_B"
    else:
        updated["phase"] = f"{mechanism}_reveal"
    return updated


def peer_round_reveal(state: Mapping, *, ccar: bool = False) -> dict:
    mechanism = "ccar" if ccar else "baseline"
    if state.get("phase") != f"{mechanism}_reveal":
        raise ValueError("Both operators must submit before reveal")
    choices = state[f"{mechanism}_choices"]
    d = state["congestion"]
    kwargs = {"ccar": True, "alpha_m": ALPHA_M} if ccar else {}
    payoff_a = utility(choices["A"], choices["B"], state["types"]["A"], d, **kwargs)
    payoff_b = utility(choices["B"], choices["A"], state["types"]["B"], d, **kwargs)
    welfare = social_welfare(
        choices["A"],
        choices["B"],
        state["types"]["A"],
        state["types"]["B"],
        d,
        accounting="underlying",
        **kwargs,
    )
    equilibrium = _benchmark(d, ccar=ccar)
    first_best = first_best_for_types(state["types"]["A"], state["types"]["B"], d)
    return {
        "types": dict(state["types"]),
        "choices": dict(choices),
        "payoff_A": payoff_a,
        "payoff_B": payoff_b,
        "underlying_social_welfare": welfare,
        "benchmark_A": equilibrium[0],
        "benchmark_B": equilibrium[1],
        "first_best_profiles": first_best.profiles,
        "first_best_welfare": first_best.welfare,
        "ccar": ccar,
    }


def format_peer_reveal(reveal: Mapping) -> str:
    best = ", ".join(
        f"A {_action_name(a)} / B {_action_name(b)}"
        for a, b in reveal["first_best_profiles"]
    )
    return (
        f"### {'CCAR' if reveal['ccar'] else 'Baseline'} peer reveal\n"
        f"- **Operator A:** {TYPE_NAMES[reveal['types']['A']]}; "
        f"{_action_name(reveal['choices']['A'])}; payoff {reveal['payoff_A']:.3f}\n"
        f"- **Operator B:** {TYPE_NAMES[reveal['types']['B']]}; "
        f"{_action_name(reveal['choices']['B'])}; payoff {reveal['payoff_B']:.3f}\n"
        f"- **Underlying social welfare:** {reveal['underlying_social_welfare']:.3f}\n\n"
        f"**Operator A benchmark:** {strategy_explanation(reveal['benchmark_A'])}.  \n"
        f"**Operator B benchmark:** {strategy_explanation(reveal['benchmark_B'])}.\n\n"
        f"- **Full-information first best:** {best}\n"
        f"- **First-best welfare:** {reveal['first_best_welfare']:.3f}\n\n"
        f"{EVIDENCE_BOUNDARY}"
    )


def begin_peer_ccar(state: Mapping) -> dict:
    if state.get("phase") != "baseline_reveal":
        raise ValueError("Complete the baseline peer reveal first")
    updated = deepcopy(dict(state))
    updated["phase"] = "ccar_A"
    return updated


def computational_results_markdown() -> str:
    """Build the displayed result summary from the copied validated model."""
    sections = ["### Under the benchmark parameterization"]
    for label, d in CONGESTION.items():
        baseline = _benchmark(d)
        ccar = _benchmark(d, ccar=True)
        bne_welfare = expected_equilibrium_welfare(baseline, d)
        ccar_welfare = expected_equilibrium_welfare(ccar, d, ccar=True, alpha_m=ALPHA_M)
        first_best = expected_first_best_welfare(d)
        sections.append(
            f"#### {label} congestion\n"
            f"- **Baseline strategy:** {strategy_explanation(baseline[0])}.\n"
            f"- **CCAR strategy:** {strategy_explanation(ccar[0])}.\n"
            f"- **BNE welfare:** {bne_welfare:.3f}\n"
            f"- **CCAR induced-outcome welfare:** {ccar_welfare:.3f}\n"
            f"- **Full-information first best:** {first_best:.3f}\n"
            f"- **Baseline welfare gap:** {first_best - bne_welfare:.3f}"
        )
    sections.append(
        "CCAR sensitivity includes regions with no equilibrium-set change, welfare improvement, "
        "excessive disclosure, increased welfare gaps, and multiple pure equilibria. These are "
        "stylized computational findings, not evidence about real firms."
    )
    return "\n\n".join(sections)


def auction_results_markdown() -> str:
    """Compute the example and Monte Carlo summary from the validated module."""
    values = {"A": 8, "B": 5, "C": 3, "D": 2}
    result = second_price_auction(values)
    simulation = simulate_truthful_comparison(rounds=10_000, n_bidders=4, seed=206)
    fcfs_efficiency = float(simulation["fcfs_efficiency"].mean())
    second_price_efficiency = float(simulation["second_price_efficiency"].mean())
    return (
        "### Verified downstream allocation results\n"
        "**Benchmark:** values A=8, B=5, C=3, D=2; FCFS order B, C, A, D.\n\n"
        "- FCFS: B wins; efficiency 0.625.\n"
        f"- Second price: {result.winner} wins; payment {result.payment:.0f}; "
        f"winner utility {result.winner_utility:.0f}; efficiency {result.allocative_efficiency:.1f}.\n\n"
        "**Monte Carlo:** 10,000 rounds, four eligible bidders, iid Uniform[0,10] values.\n\n"
        f"- FCFS mean efficiency: {fcfs_efficiency:.6f}\n"
        f"- Truthful second-price mean efficiency: {second_price_efficiency:.6f}\n\n"
        "Noisy bidding is shown only as a non-equilibrium behavioral stress test. Emergency and "
        "public-safety flights are outside this commercial auction."
    )

