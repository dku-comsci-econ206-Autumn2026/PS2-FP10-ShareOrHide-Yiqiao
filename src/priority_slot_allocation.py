"""Allocation models for one scarce low-altitude corridor priority slot.

The auction here is deliberately downstream of the strategic-disclosure model.
Emergency and public-safety flights are policy-prioritized outside these payment-
based mechanisms and are therefore reported as excluded, never ordinary bidders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


EXCLUDED_OPERATOR_TYPES = frozenset({"emergency", "public-safety", "public_safety"})


@dataclass(frozen=True)
class FCFSResult:
    """Outcome of first-come, first-served allocation."""

    winners: tuple[str, ...]
    allocated_value: float
    max_feasible_value: float
    payment: float
    winner_utility: float
    allocative_efficiency: float
    social_welfare: float
    excluded_operators: tuple[str, ...]


@dataclass(frozen=True)
class AuctionResult:
    """Outcome of a single-unit second-price sealed-bid auction."""

    winner: str
    winning_bid: float
    allocated_value: float
    highest_feasible_value: float
    second_highest_bid: float
    payment: float
    auctioneer_revenue: float
    winner_utility: float
    allocative_efficiency: float
    social_welfare: float
    excluded_operators: tuple[str, ...]


def _validate_nonnegative(mapping: Mapping[str, float], label: str) -> dict[str, float]:
    if not mapping:
        raise ValueError(f"{label} cannot be empty")
    clean = {str(name): float(number) for name, number in mapping.items()}
    if not all(np.isfinite(number) and number >= 0 for number in clean.values()):
        raise ValueError(f"{label} must be finite and nonnegative")
    return clean


def _eligibility(
    operator_ids: Sequence[str], operator_types: Mapping[str, str] | None
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return eligible and explicitly excluded IDs in the supplied order."""
    if operator_types is None:
        return tuple(operator_ids), ()
    unknown = set(operator_types).difference(operator_ids)
    if unknown:
        raise ValueError(f"operator_types contains unknown operators: {sorted(unknown)}")
    eligible: list[str] = []
    excluded: list[str] = []
    for operator_id in operator_ids:
        operator_type = operator_types.get(operator_id, "commercial").strip().lower()
        if operator_type in EXCLUDED_OPERATOR_TYPES:
            excluded.append(operator_id)
        elif operator_type == "commercial":
            eligible.append(operator_id)
        else:
            raise ValueError(f"unsupported operator type for {operator_id}: {operator_type}")
    return tuple(eligible), tuple(excluded)


def _efficiency(allocated_value: float, feasible_value: float) -> float:
    if feasible_value == 0:
        return 1.0 if allocated_value == 0 else 0.0
    efficiency = allocated_value / feasible_value
    return float(np.clip(efficiency, 0.0, 1.0))


def allocate_fcfs(
    arrival_order: Sequence[str],
    values: Mapping[str, float],
    capacity: int = 1,
    operator_types: Mapping[str, str] | None = None,
) -> FCFSResult:
    """Allocate to the first ``capacity`` eligible valid requests.

    The loop breaks as soon as capacity is filled. Payment is zero. Under the
    transfer-neutral accounting convention used here, social welfare equals the
    allocated value (there are no other modeled real resource costs).
    """
    clean_values = _validate_nonnegative(values, "values")
    if not isinstance(capacity, int) or capacity < 1:
        raise ValueError("capacity must be a positive integer")
    arrivals = tuple(str(name) for name in arrival_order)
    if len(arrivals) != len(set(arrivals)):
        raise ValueError("arrival_order cannot contain duplicate requests")
    missing = set(clean_values).difference(arrivals)
    unknown = set(arrivals).difference(clean_values)
    if missing or unknown:
        raise ValueError(
            f"arrival_order and values must name the same operators; "
            f"missing={sorted(missing)}, unknown={sorted(unknown)}"
        )

    eligible, excluded = _eligibility(arrivals, operator_types)
    eligible_set = set(eligible)
    winners: list[str] = []
    for operator_id in arrivals:
        if operator_id not in eligible_set:
            continue
        winners.append(operator_id)
        if len(winners) == capacity:
            break
    if not winners:
        raise ValueError("no eligible commercial requests remain")

    eligible_values = [clean_values[name] for name in eligible]
    feasible_count = min(capacity, len(eligible_values))
    max_feasible = float(sum(sorted(eligible_values, reverse=True)[:feasible_count]))
    allocated = float(sum(clean_values[name] for name in winners))
    return FCFSResult(
        winners=tuple(winners),
        allocated_value=allocated,
        max_feasible_value=max_feasible,
        payment=0.0,
        winner_utility=allocated,
        allocative_efficiency=_efficiency(allocated, max_feasible),
        social_welfare=allocated,
        excluded_operators=excluded,
    )


def second_price_auction(
    bids: Mapping[str, float],
    values: Mapping[str, float] | None = None,
    operator_types: Mapping[str, str] | None = None,
) -> AuctionResult:
    """Run a K=1 Vickrey auction among eligible commercial operators.

    Ties are broken deterministically by operator ID. With one eligible bidder,
    the outside bid is normalized to zero. ``values`` may differ from bids for
    bounded-rationality stress tests.
    """
    clean_bids = _validate_nonnegative(bids, "bids")
    clean_values = _validate_nonnegative(values if values is not None else bids, "values")
    if set(clean_bids) != set(clean_values):
        raise ValueError("bids and values must name the same operators")
    eligible, excluded = _eligibility(tuple(clean_bids), operator_types)
    if not eligible:
        raise ValueError("no eligible commercial bids remain")

    ranked = sorted(eligible, key=lambda name: (-clean_bids[name], name))
    winner = ranked[0]
    second_bid = clean_bids[ranked[1]] if len(ranked) > 1 else 0.0
    allocated = clean_values[winner]
    highest_feasible = max(clean_values[name] for name in eligible)
    payment = float(second_bid)
    return AuctionResult(
        winner=winner,
        winning_bid=clean_bids[winner],
        allocated_value=allocated,
        highest_feasible_value=highest_feasible,
        second_highest_bid=payment,
        payment=payment,
        auctioneer_revenue=payment,
        winner_utility=allocated - payment,
        allocative_efficiency=_efficiency(allocated, highest_feasible),
        social_welfare=allocated,
        excluded_operators=excluded,
    )


def simulate_truthful_comparison(
    rounds: int = 10_000,
    n_bidders: int = 4,
    seed: int = 206,
    value_low: float = 0.0,
    value_high: float = 10.0,
) -> dict[str, np.ndarray]:
    """Simulate FCFS and truthful Vickrey allocation on identical IPV draws."""
    if rounds < 1 or n_bidders < 2:
        raise ValueError("rounds must be positive and n_bidders must be at least two")
    if value_low < 0 or value_high <= value_low:
        raise ValueError("require 0 <= value_low < value_high")
    rng = np.random.default_rng(seed)
    values = rng.uniform(value_low, value_high, size=(rounds, n_bidders))
    arrivals = np.argsort(rng.random(size=(rounds, n_bidders)), axis=1)
    row = np.arange(rounds)
    fcfs_winner_index = arrivals[:, 0]
    fcfs_value = values[row, fcfs_winner_index]
    highest_index = np.argmax(values, axis=1)
    highest_value = values[row, highest_index]
    second_highest_value = np.partition(values, -2, axis=1)[:, -2]
    fcfs_efficiency = np.divide(
        fcfs_value,
        highest_value,
        out=np.ones_like(fcfs_value),
        where=highest_value > 0,
    )
    return {
        "values": values,
        "arrivals": arrivals,
        "fcfs_winner_index": fcfs_winner_index,
        "fcfs_allocated_value": fcfs_value,
        "fcfs_payment": np.zeros(rounds),
        "fcfs_efficiency": fcfs_efficiency,
        "fcfs_social_welfare": fcfs_value.copy(),
        "second_price_winner_index": highest_index,
        "second_price_highest_value": highest_value,
        "second_price_second_highest_value": second_highest_value,
        "second_price_payment": second_highest_value.copy(),
        "second_price_revenue": second_highest_value.copy(),
        "second_price_winner_utility": highest_value - second_highest_value,
        "second_price_efficiency": np.ones(rounds),
        "second_price_social_welfare": highest_value.copy(),
    }


def simulate_bid_noise_stress(
    rounds: int = 10_000,
    n_bidders: int = 4,
    seed: int = 1206,
    noise_sigmas: Sequence[float] = (0.0, 0.1, 0.25, 0.5, 1.0),
    value_low: float = 0.0,
    value_high: float = 10.0,
) -> list[dict[str, float | str]]:
    """Stress-test allocation under mean-one multiplicative lognormal bid noise.

    This is a behavioral perturbation, not rational equilibrium behavior. For
    sigma > 0, epsilon ~ LogNormal(-sigma^2/2, sigma), so E[epsilon] = 1, and
    bids are max(0, value * epsilon). The sigma=0 row is truthful bidding.
    """
    if rounds < 1 or n_bidders < 2:
        raise ValueError("rounds must be positive and n_bidders must be at least two")
    sigmas = tuple(float(sigma) for sigma in noise_sigmas)
    if not sigmas or any(sigma < 0 or not np.isfinite(sigma) for sigma in sigmas):
        raise ValueError("noise_sigmas must contain finite nonnegative values")
    rng = np.random.default_rng(seed)
    values = rng.uniform(value_low, value_high, size=(rounds, n_bidders))
    row = np.arange(rounds)
    highest_value = np.max(values, axis=1)
    highest_index = np.argmax(values, axis=1)
    results: list[dict[str, float | str]] = []
    for sigma in sigmas:
        if sigma == 0:
            bids = values.copy()
            label = "truthful benchmark"
        else:
            epsilon = rng.lognormal(mean=-(sigma**2) / 2, sigma=sigma, size=values.shape)
            bids = np.maximum(0.0, values * epsilon)
            label = "behavioral / bounded-rationality stress test"
        winner_index = np.argmax(bids, axis=1)
        allocated_value = values[row, winner_index]
        efficiency = np.divide(
            allocated_value,
            highest_value,
            out=np.ones_like(allocated_value),
            where=highest_value > 0,
        )
        results.append(
            {
                "behavior": label,
                "noise_sigma": sigma,
                "mean_allocative_efficiency": float(np.mean(efficiency)),
                "std_allocative_efficiency": float(np.std(efficiency, ddof=1)),
                "efficiency_q05": float(np.quantile(efficiency, 0.05)),
                "efficiency_median": float(np.median(efficiency)),
                "efficiency_q95": float(np.quantile(efficiency, 0.95)),
                "misallocation_rate": float(np.mean(winner_index != highest_index)),
            }
        )
    return results

