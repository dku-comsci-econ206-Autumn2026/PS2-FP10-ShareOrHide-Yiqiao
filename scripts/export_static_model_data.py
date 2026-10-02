#!/usr/bin/env python3
"""Export the validated finite economic model for the static HF artifact.

The browser consumes lookup records from this file; it does not reimplement the
Bayesian disclosure model or CCAR payoff formula in JavaScript.
"""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.disclosure_model import (  # noqa: E402
    ACTIONS,
    BENEFIT_SCALE,
    CONFIDENTIALITY_COSTS,
    CONGESTION,
    DISCLOSURE_LEVELS,
    LAMBDA,
    PRIVACY_COSTS,
    TYPE_PROB,
    TYPES,
    expected_equilibrium_welfare,
    expected_first_best_welfare,
    find_pure_bne,
    first_best_for_types,
    social_welfare,
    strategy_to_mapping,
    utility,
)
from src.priority_slot_allocation import (  # noqa: E402
    allocate_fcfs,
    second_price_auction,
    simulate_truthful_comparison,
)


SOURCE_COMMIT = "791e12224576e5963fd5672f8f90acdcea5556a0"
BEHAVIORAL_CHECKPOINT = "ea7ce241de34b8d21b036d39157ca974c019bb31"
ALPHA_M = 0.7
OUTPUT = ROOT / "hf_static" / "data" / "validated_model_data.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parameter_hash() -> str:
    parameters = {
        "actions": ACTIONS,
        "types": TYPES,
        "disclosure_levels": DISCLOSURE_LEVELS,
        "privacy_costs": PRIVACY_COSTS,
        "confidentiality_costs": CONFIDENTIALITY_COSTS,
        "type_probabilities": TYPE_PROB,
        "congestion": CONGESTION,
        "benefit_scale": BENEFIT_SCALE,
        "lambda": LAMBDA,
        "ccar_alpha_m": ALPHA_M,
    }
    encoded = json.dumps(parameters, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _benchmark(d: float, *, ccar: bool = False):
    kwargs = {"ccar": True, "alpha_m": ALPHA_M} if ccar else {}
    result = find_pure_bne(d, **kwargs)
    if len(result) != 1:
        raise RuntimeError("validated benchmark states must have exactly one pure BNE")
    return result.equilibria[0]


def state_key(
    mechanism: str,
    congestion_label: str,
    own_type: str,
    rival_type: str,
    own_action: str,
    rival_action: str,
) -> str:
    return "|".join(
        (mechanism, congestion_label, own_type, rival_type, own_action, rival_action)
    )


def _benchmark_block() -> dict[str, Any]:
    block: dict[str, Any] = {"baseline": {}, "ccar": {}}
    for label, d in CONGESTION.items():
        first_best = expected_first_best_welfare(d)
        for mechanism in ("baseline", "ccar"):
            is_ccar = mechanism == "ccar"
            equilibrium = _benchmark(d, ccar=is_ccar)
            kwargs = {"ccar": True, "alpha_m": ALPHA_M} if is_ccar else {}
            induced_welfare = expected_equilibrium_welfare(
                equilibrium,
                d,
                accounting="underlying",
                **kwargs,
            )
            block[mechanism][label] = {
                "d": d,
                "strategy_A": strategy_to_mapping(equilibrium[0]),
                "strategy_B": strategy_to_mapping(equilibrium[1]),
                "expected_induced_underlying_welfare": induced_welfare,
                "expected_first_best_welfare": first_best,
                "welfare_gap": first_best - induced_welfare,
            }

    expected_baseline = {
        "Low": (0.0, 0.639095),
        "Medium": (2.192883, 3.139085),
        "High": (6.881808, 7.385238),
    }
    for label, (bne, first_best) in expected_baseline.items():
        actual = block["baseline"][label]
        assert abs(actual["expected_induced_underlying_welfare"] - bne) < 1e-6
        assert abs(actual["expected_first_best_welfare"] - first_best) < 1e-6
    assert abs(
        block["ccar"]["Medium"]["expected_induced_underlying_welfare"] - 3.089085
    ) < 1e-6
    return block


def _state_index(benchmarks: dict[str, Any]) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for mechanism, (label, d), own_type, rival_type, own_action, rival_action in product(
        ("baseline", "ccar"),
        CONGESTION.items(),
        TYPES,
        TYPES,
        ACTIONS,
        ACTIONS,
    ):
        is_ccar = mechanism == "ccar"
        utility_kwargs = {"ccar": True, "alpha_m": ALPHA_M} if is_ccar else {}
        first_best = first_best_for_types(own_type, rival_type, d)
        underlying_welfare = social_welfare(
            own_action,
            rival_action,
            own_type,
            rival_type,
            d,
            accounting="underlying",
            **utility_kwargs,
        )
        key = state_key(
            mechanism,
            label,
            own_type,
            rival_type,
            own_action,
            rival_action,
        )
        records[key] = {
            "mechanism": mechanism,
            "congestion_label": label,
            "d": d,
            "own_type": own_type,
            "rival_type": rival_type,
            "own_action": own_action,
            "rival_action": rival_action,
            "own_payoff": utility(
                own_action, rival_action, own_type, d, **utility_kwargs
            ),
            "rival_payoff": utility(
                rival_action, own_action, rival_type, d, **utility_kwargs
            ),
            "underlying_social_welfare": underlying_welfare,
            "baseline_bne_action_own": benchmarks["baseline"][label]["strategy_A"][
                own_type
            ],
            "baseline_bne_action_rival": benchmarks["baseline"][label]["strategy_B"][
                rival_type
            ],
            "ccar_bne_action_own": benchmarks["ccar"][label]["strategy_A"][own_type],
            "ccar_bne_action_rival": benchmarks["ccar"][label]["strategy_B"][
                rival_type
            ],
            "first_best_profiles": [list(profile) for profile in first_best.profiles],
            "first_best_welfare": first_best.welfare,
            "welfare_gap": first_best.welfare - underlying_welfare,
        }
    return records


def _auction_block() -> dict[str, Any]:
    values = {"A": 8.0, "B": 5.0, "C": 3.0, "D": 2.0}
    arrival_order = ["B", "C", "A", "D"]
    fcfs = allocate_fcfs(arrival_order, values, capacity=1)
    second_price = second_price_auction(values, values=values)
    simulation = simulate_truthful_comparison(rounds=10_000, n_bidders=4, seed=206)

    rng = random.Random(206)
    scenarios = []
    for scenario_id in range(12):
        scenario_values = {
            "Participant": float(rng.randint(1, 10)),
            "B": float(rng.randint(1, 10)),
            "C": float(rng.randint(1, 10)),
            "D": float(rng.randint(1, 10)),
        }
        scenarios.append(
            {
                "id": scenario_id,
                "values": scenario_values,
                "rival_bids": {
                    bidder: value
                    for bidder, value in scenario_values.items()
                    if bidder != "Participant"
                },
                "setting": "Truthful IPV benchmark",
            }
        )

    return {
        "benchmark_example": {
            "values": values,
            "arrival_order": arrival_order,
            "fcfs": {
                "winner": fcfs.winners[0],
                "allocative_efficiency": fcfs.allocative_efficiency,
            },
            "second_price": {
                "winner": second_price.winner,
                "payment": second_price.payment,
                "winner_utility": second_price.winner_utility,
                "allocative_efficiency": second_price.allocative_efficiency,
            },
        },
        "monte_carlo": {
            "rounds": 10_000,
            "eligible_bidders": 4,
            "distribution": "iid Uniform[0,10]",
            "fcfs_mean_efficiency": float(simulation["fcfs_efficiency"].mean()),
            "truthful_second_price_mean_efficiency": float(
                simulation["second_price_efficiency"].mean()
            ),
        },
        "session_scenarios": scenarios,
        "excluded_operator_types": ["emergency", "public-safety"],
    }


def build_export() -> dict[str, Any]:
    benchmarks = _benchmark_block()
    state_index = _state_index(benchmarks)
    expected_count = 2 * len(CONGESTION) * len(TYPES) ** 2 * len(ACTIONS) ** 2
    if len(state_index) != expected_count:
        raise AssertionError(f"expected {expected_count} state records")

    disclosure_path = ROOT / "src" / "disclosure_model.py"
    auction_path = ROOT / "src" / "priority_slot_allocation.py"
    return {
        "metadata": {
            "source_commit": SOURCE_COMMIT,
            "behavioral_checkpoint": BEHAVIORAL_CHECKPOINT,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_parameter_hash": _parameter_hash(),
            "source_file_hashes": {
                "src/disclosure_model.py": _sha256(disclosure_path),
                "src/priority_slot_allocation.py": _sha256(auction_path),
            },
            "ccar_alpha_M": ALPHA_M,
            "stylized_parameter_warning": (
                "Numerical parameters are stylized normalized benchmarks rather than "
                "empirically calibrated estimates."
            ),
            "state_record_count": expected_count,
        },
        "labels": {
            "actions": {"M": "Minimum disclosure", "P": "Partial disclosure", "F": "Full disclosure"},
            "types": {
                "L": "Low confidentiality sensitivity",
                "H": "High confidentiality sensitivity",
            },
            "congestion": CONGESTION,
            "type_probabilities": TYPE_PROB,
            "mechanisms": ["baseline", "ccar"],
        },
        "benchmarks": benchmarks,
        "state_index": state_index,
        "auction": _auction_block(),
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = build_export()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {payload['metadata']['state_record_count']} states to {OUTPUT}")


if __name__ == "__main__":
    main()
