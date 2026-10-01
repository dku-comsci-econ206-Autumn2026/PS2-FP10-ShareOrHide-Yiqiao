"""Static Bayesian game of voluntary flight-intent disclosure.

Mandatory safety information is always available. Actions describe only the
additional commercially sensitive information disclosed voluntarily. Parameters
are stylized normalized values, not empirical monetary estimates.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping, Sequence

import numpy as np


ACTIONS = ("M", "P", "F")
TYPES = ("L", "H")
DISCLOSURE_LEVELS = {"M": 0.0, "P": 1.0, "F": 2.0}
PRIVACY_COSTS = {"M": 0.0, "P": 1.0, "F": 2.5}
CONFIDENTIALITY_COSTS = {"L": 1.0, "H": 1.6}
TYPE_PROB = {"L": 0.5, "H": 0.5}
CONGESTION = {"Low": 0.3, "Medium": 0.6, "High": 1.0}
BENEFIT_SCALE = 7.5
LAMBDA = 0.5

Strategy = tuple[str, str]
Equilibrium = tuple[Strategy, Strategy]


@dataclass(frozen=True)
class EquilibriumSearchResult:
    """All pure BNE plus an auditable candidate-profile count."""

    equilibria: tuple[Equilibrium, ...]
    profiles_checked: int

    def __iter__(self):
        return iter(self.equilibria)

    def __len__(self):
        return len(self.equilibria)


@dataclass(frozen=True)
class FirstBestResult:
    """Full-information maximizing action profiles, preserving ties."""

    profiles: tuple[tuple[str, str], ...]
    welfare: float


def _require_member(value: str, allowed: Sequence[str], label: str) -> None:
    if value not in allowed:
        raise ValueError(f"unknown {label} {value!r}; expected one of {tuple(allowed)}")


def _validate_probabilities(type_prob: Mapping[str, float]) -> None:
    if set(type_prob) != set(TYPES):
        raise ValueError(f"type probabilities must be defined for {TYPES}")
    if any(probability < 0 for probability in type_prob.values()):
        raise ValueError("type probabilities must be nonnegative")
    if not np.isclose(sum(type_prob.values()), 1.0):
        raise ValueError("type probabilities must sum to one")


def strategy_to_mapping(strategy: Strategy) -> dict[str, str]:
    """Map a tuple ordered as (low-type action, high-type action)."""
    if len(strategy) != len(TYPES):
        raise ValueError("a strategy must specify one action for each type")
    for action in strategy:
        _require_member(action, ACTIONS, "action")
    return dict(zip(TYPES, strategy, strict=True))


def all_pure_strategies() -> tuple[Strategy, ...]:
    """Generate all 3^2 type-contingent pure strategies."""
    return tuple(product(ACTIONS, repeat=len(TYPES)))


def coordination_benefit(
    action_i: str,
    action_j: str,
    congestion: float,
    disclosure_levels: Mapping[str, float] = DISCLOSURE_LEVELS,
    benefit_scale: float = BENEFIT_SCALE,
    decay: float = LAMBDA,
) -> float:
    """Return d*B*[1-exp(-lambda*(x_i+x_j))]."""
    _require_member(action_i, ACTIONS, "action")
    _require_member(action_j, ACTIONS, "action")
    if congestion < 0 or benefit_scale < 0 or decay < 0:
        raise ValueError("congestion, benefit_scale, and decay must be nonnegative")
    total_disclosure = disclosure_levels[action_i] + disclosure_levels[action_j]
    return float(congestion * benefit_scale * (1.0 - np.exp(-decay * total_disclosure)))


def privacy_cost(
    action: str,
    confidentiality_type: str,
    confidentiality_costs: Mapping[str, float] = CONFIDENTIALITY_COSTS,
    privacy_costs: Mapping[str, float] = PRIVACY_COSTS,
) -> float:
    """Return c_i*k(a_i), the voluntary commercial-confidentiality cost."""
    _require_member(action, ACTIONS, "action")
    _require_member(confidentiality_type, TYPES, "type")
    return float(confidentiality_costs[confidentiality_type] * privacy_costs[action])


def access_factor(
    action: str,
    congestion: float,
    alpha_m: float = 0.7,
    ccar: bool = False,
) -> float:
    """CCAR access to enhanced non-safety coordination information.

    Low congestion leaves access unchanged. At Medium/High benchmark states,
    Minimum disclosure receives alpha_m while Partial and Full receive one.
    """
    _require_member(action, ACTIONS, "action")
    if not 0 <= alpha_m <= 1:
        raise ValueError("alpha_m must lie in [0,1]")
    if not ccar or congestion <= CONGESTION["Low"] + 1e-12 or action != "M":
        return 1.0
    return float(alpha_m)


def utility(
    action_i: str,
    action_j: str,
    confidentiality_type_i: str,
    congestion: float,
    *,
    confidentiality_costs: Mapping[str, float] = CONFIDENTIALITY_COSTS,
    privacy_costs: Mapping[str, float] = PRIVACY_COSTS,
    disclosure_levels: Mapping[str, float] = DISCLOSURE_LEVELS,
    benefit_scale: float = BENEFIT_SCALE,
    decay: float = LAMBDA,
    ccar: bool = False,
    alpha_m: float = 0.7,
) -> float:
    """Compute baseline or CCAR operator utility directly from primitives."""
    benefit = coordination_benefit(
        action_i,
        action_j,
        congestion,
        disclosure_levels=disclosure_levels,
        benefit_scale=benefit_scale,
        decay=decay,
    )
    return float(
        access_factor(action_i, congestion, alpha_m=alpha_m, ccar=ccar) * benefit
        - privacy_cost(
            action_i,
            confidentiality_type_i,
            confidentiality_costs=confidentiality_costs,
            privacy_costs=privacy_costs,
        )
    )


def payoff_matrix(
    type_a: str,
    type_b: str,
    congestion: float,
    **utility_kwargs,
) -> dict[tuple[str, str], tuple[float, float]]:
    """Generate a 3x3 complete-information payoff matrix programmatically."""
    _require_member(type_a, TYPES, "type")
    _require_member(type_b, TYPES, "type")
    matrix: dict[tuple[str, str], tuple[float, float]] = {}
    for action_a, action_b in product(ACTIONS, repeat=2):
        matrix[(action_a, action_b)] = (
            utility(action_a, action_b, type_a, congestion, **utility_kwargs),
            utility(action_b, action_a, type_b, congestion, **utility_kwargs),
        )
    return matrix


def expected_utility_action(
    action: str,
    own_type: str,
    opponent_strategy: Strategy,
    congestion: float,
    *,
    type_prob: Mapping[str, float] = TYPE_PROB,
    **utility_kwargs,
) -> float:
    """Expected utility of one action against a type-contingent rival strategy."""
    _require_member(action, ACTIONS, "action")
    _require_member(own_type, TYPES, "type")
    _validate_probabilities(type_prob)
    opponent = strategy_to_mapping(opponent_strategy)
    return float(
        sum(
            type_prob[opponent_type]
            * utility(action, opponent[opponent_type], own_type, congestion, **utility_kwargs)
            for opponent_type in TYPES
        )
    )


def is_best_response_strategy(
    strategy: Strategy,
    opponent_strategy: Strategy,
    congestion: float,
    *,
    tolerance: float = 1e-10,
    type_prob: Mapping[str, float] = TYPE_PROB,
    **utility_kwargs,
) -> bool:
    """Check interim optimality separately for both own types."""
    own = strategy_to_mapping(strategy)
    for own_type in TYPES:
        action_values = {
            action: expected_utility_action(
                action,
                own_type,
                opponent_strategy,
                congestion,
                type_prob=type_prob,
                **utility_kwargs,
            )
            for action in ACTIONS
        }
        if action_values[own[own_type]] < max(action_values.values()) - tolerance:
            return False
    return True


def find_pure_bne(
    congestion: float,
    *,
    tolerance: float = 1e-10,
    type_prob: Mapping[str, float] = TYPE_PROB,
    **utility_kwargs,
) -> EquilibriumSearchResult:
    """Enumerate all 9x9 strategy profiles; symmetry is never imposed."""
    strategies = all_pure_strategies()
    equilibria: list[Equilibrium] = []
    profiles_checked = 0
    for strategy_a, strategy_b in product(strategies, repeat=2):
        profiles_checked += 1
        if is_best_response_strategy(
            strategy_a,
            strategy_b,
            congestion,
            tolerance=tolerance,
            type_prob=type_prob,
            **utility_kwargs,
        ) and is_best_response_strategy(
            strategy_b,
            strategy_a,
            congestion,
            tolerance=tolerance,
            type_prob=type_prob,
            **utility_kwargs,
        ):
            equilibria.append((strategy_a, strategy_b))
    return EquilibriumSearchResult(tuple(equilibria), profiles_checked)


def social_welfare(
    action_a: str,
    action_b: str,
    type_a: str,
    type_b: str,
    congestion: float,
    *,
    accounting: str = "underlying",
    **utility_kwargs,
) -> float:
    """Sum operator utilities under an explicit welfare convention.

    ``underlying`` always values coordination using unrestricted baseline benefit,
    so a CCAR access penalty is not mistaken for a real social loss or gain.
    ``operator`` sums the actual utilities, including CCAR access factors.
    There are no payments in this disclosure model.
    """
    if accounting not in {"underlying", "operator"}:
        raise ValueError("accounting must be 'underlying' or 'operator'")
    operator_kwargs = dict(utility_kwargs)
    if accounting == "underlying":
        operator_kwargs["ccar"] = False
    return float(
        utility(action_a, action_b, type_a, congestion, **operator_kwargs)
        + utility(action_b, action_a, type_b, congestion, **operator_kwargs)
    )


def first_best_for_types(
    type_a: str,
    type_b: str,
    congestion: float,
    *,
    tolerance: float = 1e-10,
    **welfare_kwargs,
) -> FirstBestResult:
    """Full-information first best for realized types, with all ties retained."""
    outcomes = {
        profile: social_welfare(*profile, type_a, type_b, congestion, **welfare_kwargs)
        for profile in product(ACTIONS, repeat=2)
    }
    best_welfare = max(outcomes.values())
    best_profiles = tuple(
        profile
        for profile, welfare in outcomes.items()
        if np.isclose(welfare, best_welfare, atol=tolerance, rtol=0.0)
    )
    return FirstBestResult(best_profiles, float(best_welfare))


def expected_equilibrium_welfare(
    equilibrium: Equilibrium,
    congestion: float,
    *,
    type_prob: Mapping[str, float] = TYPE_PROB,
    accounting: str = "underlying",
    **welfare_kwargs,
) -> float:
    """Ex-ante welfare of a type-contingent equilibrium strategy profile."""
    _validate_probabilities(type_prob)
    strategy_a, strategy_b = map(strategy_to_mapping, equilibrium)
    total = 0.0
    for type_a, type_b in product(TYPES, repeat=2):
        total += (
            type_prob[type_a]
            * type_prob[type_b]
            * social_welfare(
                strategy_a[type_a],
                strategy_b[type_b],
                type_a,
                type_b,
                congestion,
                accounting=accounting,
                **welfare_kwargs,
            )
        )
    return float(total)


def expected_first_best_welfare(
    congestion: float,
    *,
    type_prob: Mapping[str, float] = TYPE_PROB,
    **welfare_kwargs,
) -> float:
    """Expected full-information first-best welfare before types are realized."""
    _validate_probabilities(type_prob)
    return float(
        sum(
            type_prob[type_a]
            * type_prob[type_b]
            * first_best_for_types(
                type_a,
                type_b,
                congestion,
                **welfare_kwargs,
            ).welfare
            for type_a, type_b in product(TYPES, repeat=2)
        )
    )


def expected_equilibrium_disclosure(
    equilibrium: Equilibrium,
    *,
    type_prob: Mapping[str, float] = TYPE_PROB,
    disclosure_levels: Mapping[str, float] = DISCLOSURE_LEVELS,
) -> float:
    """Expected total disclosure units generated by an equilibrium."""
    _validate_probabilities(type_prob)
    strategy_a, strategy_b = map(strategy_to_mapping, equilibrium)
    return float(
        sum(
            type_prob[type_a]
            * type_prob[type_b]
            * (
                disclosure_levels[strategy_a[type_a]]
                + disclosure_levels[strategy_b[type_b]]
            )
            for type_a, type_b in product(TYPES, repeat=2)
        )
    )


def expected_first_best_disclosure(
    congestion: float,
    *,
    type_prob: Mapping[str, float] = TYPE_PROB,
    disclosure_levels: Mapping[str, float] = DISCLOSURE_LEVELS,
    tie_rule: str = "mean",
    **welfare_kwargs,
) -> float:
    """Expected total first-best disclosure, averaging across tied optima by default."""
    if tie_rule != "mean":
        raise ValueError("only the explicit 'mean' tie rule is supported")
    _validate_probabilities(type_prob)
    total = 0.0
    for type_a, type_b in product(TYPES, repeat=2):
        result = first_best_for_types(type_a, type_b, congestion, **welfare_kwargs)
        disclosure = np.mean(
            [disclosure_levels[a] + disclosure_levels[b] for a, b in result.profiles]
        )
        total += type_prob[type_a] * type_prob[type_b] * disclosure
    return float(total)


def equilibrium_label(equilibrium: Equilibrium) -> str:
    """Compact, unambiguous label: A(L,H)|B(L,H)."""
    return f"A{equilibrium[0]}|B{equilibrium[1]}"

