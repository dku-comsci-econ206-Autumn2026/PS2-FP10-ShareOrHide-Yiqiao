"""Build the core strategic-disclosure notebook from auditable source cells."""

from pathlib import Path

import nbformat as nbf

from notebook_bootstrap import BOOTSTRAP_SOURCE


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "01_strategic_disclosure_game.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


cells = [
    md(
        r"""
# Share or Hide? Strategic Disclosure in Congested Low-Altitude Drone Traffic

## Research question

> When competing drone operators have privately known commercial-confidentiality costs, how much flight-intent information will they strategically disclose as low-altitude traffic congestion changes, and when does the resulting equilibrium disclosure differ from the socially desirable level?

The focus is **endogenous disclosure granularity + private commercial-confidentiality sensitivity + congestion-dependent information value**. This notebook does not claim to invent privacy-aware UTM, airspace auctions, or reciprocal information sharing.

## Model boundary

This is a **static Bayesian game with incomplete information** and simultaneous actions. The solution concept is pure-strategy Bayesian Nash equilibrium (BNE), not SPNE or PBE. Parameters are stylized normalized values—not empirical estimates or dollar amounts.

Mandatory safety information is always assumed available. Minimum disclosure (`M`) means only mandatory/basic information; it never means withholding legally required safety information. The voluntary choices are:

- `M`: mandatory/basic information only;
- `P`: next sector, coarse ETA, approximate traffic volume;
- `F`: richer route, timing, and trajectory information.
"""
    ),
    md(
        r"""
## Players, types, public state, and utility

Players are $N=\{A,B\}$. Each independently draws confidentiality type $c_i\in\{c_L,c_H\}$, observes its own type, and has prior probability 0.5 on each rival type. `L` means low confidentiality sensitivity and `H` high sensitivity. Congestion $d$ is public.

For actions $a_i,a_j\in\{M,P,F\}$,

$$CB_i(a_i,a_j,d)=dB\left[1-\exp\{-\lambda(x_i+x_j)\}\right],$$

$$PC_i(a_i,c_i)=c_i k(a_i),$$

$$u_i(a_i,a_j;c_i,d)=CB_i(a_i,a_j,d)-PC_i(a_i,c_i).$$

Benchmark primitives are imported from the reusable module rather than reconstructed in the notebook.
"""
    ),
    code(
        BOOTSTRAP_SOURCE
        + r"""

import csv
import importlib.metadata as metadata
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.disclosure_model import (
    ACTIONS,
    BENEFIT_SCALE,
    CONFIDENTIALITY_COSTS,
    CONGESTION,
    DISCLOSURE_LEVELS,
    LAMBDA,
    PRIVACY_COSTS,
    TYPE_PROB,
    TYPES,
    all_pure_strategies,
    coordination_benefit,
    equilibrium_label,
    expected_equilibrium_disclosure,
    expected_equilibrium_welfare,
    expected_first_best_disclosure,
    expected_first_best_welfare,
    expected_utility_action,
    find_pure_bne,
    first_best_for_types,
    payoff_matrix,
    social_welfare,
    utility,
)

TABLE_DIR = ROOT / "outputs" / "tables"
FIGURE_DIR = ROOT / "outputs" / "figures"
TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
ALPHA_M = 0.7
TOL = 1e-10

def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def strategy_text(strategy):
    return f"({strategy[0]},{strategy[1]})"

def save_figure(fig, stem):
    for extension in ("png", "svg"):
        fig.savefig(FIGURE_DIR / f"{stem}.{extension}", dpi=180, bbox_inches="tight")
    plt.close(fig)

print("Actions:", ACTIONS)
print("Types:", TYPES)
print("x:", DISCLOSURE_LEVELS)
print("k:", PRIVACY_COSTS)
print("c:", CONFIDENTIALITY_COSTS)
print("type probabilities:", TYPE_PROB)
print("congestion:", CONGESTION)
print("B, lambda:", BENEFIT_SCALE, LAMBDA)
"""
    ),
    md("## Direct numerical validation and complete-information payoff matrices"),
    code(
        r"""
required_utility = utility("P", "P", "L", 1.0)
assert np.isclose(required_utility, 3.7409041912141827, atol=1e-9)
print(f"utility(P,P,L,High) = {required_utility:.9f}")

payoff_rows = []
for type_pair_label, type_a, type_b in [("L/L", "L", "L"), ("L/H", "L", "H")]:
    matrix = payoff_matrix(type_a, type_b, CONGESTION["Medium"])
    print(f"Medium-congestion {type_pair_label} payoff matrix; rows=A, columns=B")
    print("       ", "  ".join(f"B={action:>12}" for action in ACTIONS))
    for action_a in ACTIONS:
        cells = [f"({matrix[(action_a, action_b)][0]:.3f},{matrix[(action_a, action_b)][1]:.3f})" for action_b in ACTIONS]
        print(f"A={action_a}:  " + "  ".join(f"{cell:>12}" for cell in cells))
        for action_b in ACTIONS:
            payoff_a, payoff_b = matrix[(action_a, action_b)]
            payoff_rows.append({
                "type_pair": type_pair_label,
                "congestion": "Medium",
                "action_A": action_a,
                "action_B": action_b,
                "payoff_A": payoff_a,
                "payoff_B": payoff_b,
            })
write_csv(TABLE_DIR / "payoff_matrices_medium.csv", payoff_rows)
"""
    ),
    md(
        r"""
## Bayesian strategies and the interim expected-utility check

A pure Bayesian strategy maps an operator's own type to an action: $s_i:\{L,H\}\rightarrow\{M,P,F\}$. The tuple order is always `(low-type action, high-type action)`. Thus `(P,M)` means **Low type $\rightarrow$ Partial; High type $\rightarrow$ Minimum**. It does not mean Operator A chooses P and Operator B chooses M.
"""
    ),
    code(
        r"""
strategies = all_pure_strategies()
assert len(strategies) == 9
print("All nine strategies:", strategies)

expected_utility_rows = []
opponent_strategy = ("P", "M")
for own_type in TYPES:
    for action in ACTIONS:
        value = expected_utility_action(
            action, own_type, opponent_strategy, CONGESTION["Medium"]
        )
        expected_utility_rows.append({
            "own_type": own_type,
            "own_action": action,
            "opponent_strategy_L_H": strategy_text(opponent_strategy),
            "expected_utility": value,
        })
        print(f"type={own_type}, action={action}: {value:.3f}")
write_csv(TABLE_DIR / "expected_utility_check.csv", expected_utility_rows)
"""
    ),
    md(
        r"""
## All pure Bayesian Nash equilibria

The search evaluates all $9\times9=81$ strategy-profile pairs and does not impose symmetry. Every listed tuple is type-contingent in `(L,H)` order.
"""
    ),
    code(
        r"""
baseline_results = {}
baseline_bne_rows = []
for congestion_label, d in CONGESTION.items():
    result = find_pure_bne(d)
    assert result.profiles_checked == 81
    baseline_results[congestion_label] = result
    for equilibrium_index, (strategy_a, strategy_b) in enumerate(result, start=1):
        baseline_bne_rows.append({
            "Congestion": congestion_label,
            "d": d,
            "Equilibrium index": equilibrium_index,
            "Operator A low-type action": strategy_a[0],
            "Operator A high-type action": strategy_a[1],
            "Operator B low-type action": strategy_b[0],
            "Operator B high-type action": strategy_b[1],
            "Number of pure BNE": len(result),
            "Candidate profiles checked": result.profiles_checked,
        })
    print(congestion_label, [equilibrium_label(eq) for eq in result])

expected_bne = {
    "Low": (("M", "M"), ("M", "M")),
    "Medium": (("P", "M"), ("P", "M")),
    "High": (("P", "P"), ("P", "P")),
}
for label, result in baseline_results.items():
    assert result.equilibria == (expected_bne[label],)

write_csv(TABLE_DIR / "baseline_bne_summary.csv", baseline_bne_rows)
"""
    ),
    md(
        r"""
## Full-information first best and expected welfare

Baseline social welfare is boundedly defined as $W=u_A+u_B$. There are no payments. For every congestion and realized type pair, a planner who observes both types enumerates all nine action profiles. This is a **full-information first best**, not automatically an implementable social optimum. All maximizing ties within numerical tolerance are retained.
"""
    ),
    code(
        r"""
first_best_rows = []
welfare_rows = []
for congestion_label, d in CONGESTION.items():
    for type_a in TYPES:
        for type_b in TYPES:
            result = first_best_for_types(type_a, type_b, d)
            first_best_rows.append({
                "Congestion": congestion_label,
                "d": d,
                "type_A": type_a,
                "type_B": type_b,
                "maximizing_profiles": ";".join(f"({a},{b})" for a, b in result.profiles),
                "number_of_tied_maximizers": len(result.profiles),
                "first_best_welfare": result.welfare,
            })
    equilibrium = baseline_results[congestion_label].equilibria[0]
    bne_welfare = expected_equilibrium_welfare(equilibrium, d)
    first_best_welfare = expected_first_best_welfare(d)
    welfare_rows.append({
        "Congestion": congestion_label,
        "d": d,
        "BNE welfare": bne_welfare,
        "Full-information first-best welfare": first_best_welfare,
        "Welfare gap": first_best_welfare - bne_welfare,
    })
    print(
        f"{congestion_label}: BNE={bne_welfare:.3f}, "
        f"first best={first_best_welfare:.3f}, gap={first_best_welfare-bne_welfare:.3f}"
    )

write_csv(TABLE_DIR / "first_best_by_type.csv", first_best_rows)
write_csv(TABLE_DIR / "baseline_welfare_gap.csv", welfare_rows)
"""
    ),
    code(
        r"""
plt.style.use("seaborn-v0_8-whitegrid")
labels = [row["Congestion"] for row in welfare_rows]
x_positions = np.arange(len(labels))
bne_values = [row["BNE welfare"] for row in welfare_rows]
fb_values = [row["Full-information first-best welfare"] for row in welfare_rows]
gaps = [row["Welfare gap"] for row in welfare_rows]

fig, ax = plt.subplots(figsize=(7.0, 4.4))
width = 0.36
ax.bar(x_positions - width/2, bne_values, width, label="Bayesian equilibrium", color="#4C78A8")
ax.bar(x_positions + width/2, fb_values, width, label="Full-information first best", color="#F58518")
ax.set_xticks(x_positions, labels)
ax.set_ylabel("Expected welfare (normalized units)")
ax.set_title("Equilibrium and full-information first-best welfare")
ax.legend(frameon=False)
save_figure(fig, "baseline_welfare_comparison")

fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.plot(labels, gaps, marker="o", linewidth=2, color="#E45756")
ax.set_ylim(bottom=0)
ax.set_ylabel("Expected welfare gap")
ax.set_title("Full-information first best minus Bayesian equilibrium")
for index, value in enumerate(gaps):
    ax.text(index, value + 0.025, f"{value:.3f}", ha="center")
save_figure(fig, "baseline_welfare_gap")
"""
    ),
    md(
        r"""
## Candidate mechanism: Congestion-Contingent Access Rule (CCAR)

CCAR never conditions mandatory safety information. It affects only access to enhanced non-safety coordination information. At Low congestion, $\alpha(M)=\alpha(P)=\alpha(F)=1$. At Medium and High, $\alpha(P)=\alpha(F)=1$ and $\alpha(M)=\alpha_M$; the initial benchmark is $\alpha_M=0.7$.

Operator utility under CCAR is

$$u_i^{CCAR}=\alpha(a_i,d)dB[1-\exp\{-\lambda(x_i+x_j)\}]-c_i k(a_i).$$

CCAR is a candidate mechanism, not a novelty or universal-superiority claim. Equilibrium behavior uses CCAR operator utility. Welfare comparisons use the **same underlying social value of disclosure as the baseline**, excluding the artificial access penalty; operator utility including the restriction is reported separately. This prevents a bookkeeping change from masquerading as a welfare gain.
"""
    ),
    code(
        r"""
ccar_bne_rows = []
ccar_benchmark = {}
for congestion_label, d in CONGESTION.items():
    result = find_pure_bne(d, ccar=True, alpha_m=ALPHA_M)
    ccar_benchmark[congestion_label] = result
    for equilibrium_index, equilibrium in enumerate(result, start=1):
        strategy_a, strategy_b = equilibrium
        ccar_bne_rows.append({
            "Congestion": congestion_label,
            "d": d,
            "alpha_M": ALPHA_M,
            "Equilibrium index": equilibrium_index,
            "A strategy (L,H)": strategy_text(strategy_a),
            "B strategy (L,H)": strategy_text(strategy_b),
            "Number of pure BNE": len(result),
            "Underlying expected welfare": expected_equilibrium_welfare(
                equilibrium, d, ccar=True, alpha_m=ALPHA_M
            ),
            "CCAR operator-utility sum": expected_equilibrium_welfare(
                equilibrium, d, accounting="operator", ccar=True, alpha_m=ALPHA_M
            ),
            "Full-information first-best welfare": expected_first_best_welfare(d),
        })
    print(congestion_label, [equilibrium_label(eq) for eq in result])

expected_ccar = {
    "Low": (("M", "M"), ("M", "M")),
    "Medium": (("P", "P"), ("P", "P")),
    "High": (("P", "P"), ("P", "P")),
}
for label, result in ccar_benchmark.items():
    assert result.equilibria == (expected_ccar[label],)
write_csv(TABLE_DIR / "ccar_bne_summary.csv", ccar_bne_rows)
"""
    ),
    md("## CCAR $\\alpha_M$ sensitivity: grid thresholds are approximate, not analytical"),
    code(
        r"""
alpha_values = np.round(np.arange(0.50, 1.0001, 0.05), 2)
alpha_rows = []
for congestion_label in ("Medium", "High"):
    d = CONGESTION[congestion_label]
    previous_set = None
    for alpha_m in alpha_values:
        result = find_pure_bne(d, ccar=True, alpha_m=float(alpha_m))
        equilibrium_set = tuple(equilibrium_label(eq) for eq in result)
        switched = previous_set is not None and equilibrium_set != previous_set
        if result.equilibria:
            for equilibrium_index, equilibrium in enumerate(result, start=1):
                strategy_a, strategy_b = equilibrium
                welfare = expected_equilibrium_welfare(
                    equilibrium, d, ccar=True, alpha_m=float(alpha_m)
                )
                alpha_rows.append({
                    "Congestion": congestion_label,
                    "d": d,
                    "alpha_M": alpha_m,
                    "Equilibrium index": equilibrium_index,
                    "A strategy (L,H)": strategy_text(strategy_a),
                    "B strategy (L,H)": strategy_text(strategy_b),
                    "Underlying expected welfare": welfare,
                    "CCAR operator-utility sum": expected_equilibrium_welfare(
                        equilibrium,
                        d,
                        accounting="operator",
                        ccar=True,
                        alpha_m=float(alpha_m),
                    ),
                    "Full-information first-best welfare": expected_first_best_welfare(d),
                    "Welfare gap": expected_first_best_welfare(d) - welfare,
                    "Number of pure BNE": len(result),
                    "Equilibrium set switched from prior grid point": switched,
                })
        else:
            alpha_rows.append({
                "Congestion": congestion_label,
                "d": d,
                "alpha_M": alpha_m,
                "Equilibrium index": "",
                "A strategy (L,H)": "",
                "B strategy (L,H)": "",
                "Underlying expected welfare": "",
                "CCAR operator-utility sum": "",
                "Full-information first-best welfare": expected_first_best_welfare(d),
                "Welfare gap": "",
                "Number of pure BNE": 0,
                "Equilibrium set switched from prior grid point": switched,
            })
        if switched:
            print(
                f"{congestion_label}: equilibrium set changes between the previous grid point "
                f"and alpha_M={alpha_m:.2f}; this is only a grid threshold."
            )
        previous_set = equilibrium_set
write_csv(TABLE_DIR / "ccar_alpha_sensitivity.csv", alpha_rows)
"""
    ),
    md("## Confidentiality sensitivity and equilibrium phase diagram"),
    code(
        r"""
c_high_values = np.round(np.arange(1.1, 3.0001, 0.1), 1)
confidentiality_rows = []
phase_sets = {}
for mechanism in ("Baseline", "CCAR"):
    for congestion_label, d in CONGESTION.items():
        for c_high in c_high_values:
            confidentiality_costs = {"L": 1.0, "H": float(c_high)}
            kwargs = {"confidentiality_costs": confidentiality_costs}
            if mechanism == "CCAR":
                kwargs.update({"ccar": True, "alpha_m": ALPHA_M})
            result = find_pure_bne(d, **kwargs)
            phase_sets[(mechanism, congestion_label, c_high)] = "; ".join(
                equilibrium_label(eq) for eq in result
            ) or "No pure BNE"
            if result.equilibria:
                for equilibrium_index, equilibrium in enumerate(result, start=1):
                    welfare = expected_equilibrium_welfare(equilibrium, d, **kwargs)
                    confidentiality_rows.append({
                        "Mechanism": mechanism,
                        "Congestion": congestion_label,
                        "d": d,
                        "c_L": 1.0,
                        "c_H": c_high,
                        "alpha_M": ALPHA_M if mechanism == "CCAR" else 1.0,
                        "Equilibrium index": equilibrium_index,
                        "A strategy (L,H)": strategy_text(equilibrium[0]),
                        "B strategy (L,H)": strategy_text(equilibrium[1]),
                        "Underlying expected welfare": welfare,
                        "Full-information first-best welfare": expected_first_best_welfare(
                            d, confidentiality_costs=confidentiality_costs
                        ),
                        "Number of pure BNE": len(result),
                    })
            else:
                confidentiality_rows.append({
                    "Mechanism": mechanism,
                    "Congestion": congestion_label,
                    "d": d,
                    "c_L": 1.0,
                    "c_H": c_high,
                    "alpha_M": ALPHA_M if mechanism == "CCAR" else 1.0,
                    "Equilibrium index": "",
                    "A strategy (L,H)": "",
                    "B strategy (L,H)": "",
                    "Underlying expected welfare": "",
                    "Full-information first-best welfare": expected_first_best_welfare(
                        d, confidentiality_costs=confidentiality_costs
                    ),
                    "Number of pure BNE": 0,
                })
write_csv(TABLE_DIR / "confidentiality_sensitivity.csv", confidentiality_rows)

all_phase_labels = sorted(set(phase_sets.values()))
phase_code = {label: index for index, label in enumerate(all_phase_labels)}
fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.5), sharex=True)
colors = {"Low": "#4C78A8", "Medium": "#F58518", "High": "#54A24B"}
for ax, mechanism in zip(axes, ("Baseline", "CCAR"), strict=True):
    for congestion_label in CONGESTION:
        y_values = [phase_code[phase_sets[(mechanism, congestion_label, value)]] for value in c_high_values]
        ax.step(c_high_values, y_values, where="mid", label=congestion_label, color=colors[congestion_label])
    ax.set_title(mechanism)
    ax.set_yticks(range(len(all_phase_labels)), all_phase_labels, fontsize=7)
    ax.set_ylabel("Pure-BNE set")
    ax.legend(frameon=False, ncol=3)
axes[-1].set_xlabel("High-type confidentiality sensitivity $c_H$ ($c_L=1$)")
fig.suptitle("Equilibrium phase diagram under confidentiality sensitivity", y=1.01)
fig.tight_layout()
save_figure(fig, "confidentiality_equilibrium_phase")
"""
    ),
    md("## Full-disclosure cost robustness"),
    code(
        r"""
k_full_values = np.round(np.arange(1.2, 3.5001, 0.1), 1)
full_rows = []
for mechanism in ("Baseline", "CCAR"):
    for congestion_label, d in CONGESTION.items():
        for k_full in k_full_values:
            privacy_costs = dict(PRIVACY_COSTS)
            privacy_costs["F"] = float(k_full)
            kwargs = {"privacy_costs": privacy_costs}
            if mechanism == "CCAR":
                kwargs.update({"ccar": True, "alpha_m": ALPHA_M})
            result = find_pure_bne(d, **kwargs)
            full_best_response = False
            for opponent_strategy in all_pure_strategies():
                for own_type in TYPES:
                    action_values = {
                        action: expected_utility_action(
                            action, own_type, opponent_strategy, d, **kwargs
                        )
                        for action in ACTIONS
                    }
                    if action_values["F"] >= max(action_values.values()) - TOL:
                        full_best_response = True
            if result.equilibria:
                for equilibrium_index, equilibrium in enumerate(result, start=1):
                    full_rows.append({
                        "Mechanism": mechanism,
                        "Congestion": congestion_label,
                        "d": d,
                        "k_F": k_full,
                        "Equilibrium index": equilibrium_index,
                        "A strategy (L,H)": strategy_text(equilibrium[0]),
                        "B strategy (L,H)": strategy_text(equilibrium[1]),
                        "Full appears in equilibrium": any(
                            action == "F" for strategy in equilibrium for action in strategy
                        ),
                        "Full is a best response somewhere": full_best_response,
                        "Underlying expected welfare": expected_equilibrium_welfare(
                            equilibrium, d, **kwargs
                        ),
                        "Number of pure BNE": len(result),
                    })
            else:
                full_rows.append({
                    "Mechanism": mechanism,
                    "Congestion": congestion_label,
                    "d": d,
                    "k_F": k_full,
                    "Equilibrium index": "",
                    "A strategy (L,H)": "",
                    "B strategy (L,H)": "",
                    "Full appears in equilibrium": False,
                    "Full is a best response somewhere": full_best_response,
                    "Underlying expected welfare": "",
                    "Number of pure BNE": 0,
                })
write_csv(TABLE_DIR / "full_disclosure_sensitivity.csv", full_rows)

for mechanism in ("Baseline", "CCAR"):
    for congestion_label in CONGESTION:
        relevant = [
            row for row in full_rows
            if row["Mechanism"] == mechanism
            and row["Congestion"] == congestion_label
            and row["Full appears in equilibrium"]
        ]
        if relevant:
            print(
                mechanism,
                congestion_label,
                "Full appears in equilibrium on the tested grid for k_F up to",
                max(row["k_F"] for row in relevant),
            )
"""
    ),
    md(
        r"""
## Mechanism failure-region search

This diagnostic searches a broader grid: $\alpha_M\in\{0.10,0.15,\ldots,1.00\}$, $c_H\in\{1.1,1.2,\ldots,3.0\}$, at Medium and High congestion with benchmark $k(F)$. “Robust welfare improvement” means the worst CCAR pure-BNE welfare exceeds the best baseline pure-BNE welfare. “Excessive disclosure” means at least one CCAR equilibrium has expected disclosure above the mean disclosure across tied full-information first-best profiles. “Increased gap” flags any CCAR equilibrium whose gap exceeds the worst baseline-equilibrium gap. These are transparent grid diagnostics, not analytical global results.
"""
    ),
    code(
        r"""
failure_rows = []
failure_alpha_values = np.round(np.arange(0.10, 1.0001, 0.05), 2)
for congestion_label in ("Medium", "High"):
    d = CONGESTION[congestion_label]
    for c_high in c_high_values:
        confidentiality_costs = {"L": 1.0, "H": float(c_high)}
        baseline = find_pure_bne(d, confidentiality_costs=confidentiality_costs)
        baseline_welfare = [
            expected_equilibrium_welfare(
                equilibrium, d, confidentiality_costs=confidentiality_costs
            )
            for equilibrium in baseline
        ]
        baseline_disclosure = [expected_equilibrium_disclosure(eq) for eq in baseline]
        first_best_welfare = expected_first_best_welfare(
            d, confidentiality_costs=confidentiality_costs
        )
        first_best_disclosure = expected_first_best_disclosure(
            d, confidentiality_costs=confidentiality_costs
        )
        for alpha_m in failure_alpha_values:
            ccar = find_pure_bne(
                d,
                confidentiality_costs=confidentiality_costs,
                ccar=True,
                alpha_m=float(alpha_m),
            )
            ccar_welfare = [
                expected_equilibrium_welfare(
                    equilibrium,
                    d,
                    confidentiality_costs=confidentiality_costs,
                    ccar=True,
                    alpha_m=float(alpha_m),
                )
                for equilibrium in ccar
            ]
            ccar_disclosure = [expected_equilibrium_disclosure(eq) for eq in ccar]
            no_effect = set(baseline.equilibria) == set(ccar.equilibria)
            robust_improvement = bool(
                baseline_welfare
                and ccar_welfare
                and min(ccar_welfare) > max(baseline_welfare) + TOL
            )
            excessive = bool(
                ccar_disclosure
                and max(ccar_disclosure) > first_best_disclosure + TOL
            )
            increased_gap = bool(
                baseline_welfare
                and ccar_welfare
                and max(first_best_welfare - value for value in ccar_welfare)
                > max(first_best_welfare - value for value in baseline_welfare) + TOL
            )
            failure_rows.append({
                "Congestion": congestion_label,
                "d": d,
                "c_H": c_high,
                "alpha_M": alpha_m,
                "Baseline pure BNE": ";".join(equilibrium_label(eq) for eq in baseline),
                "CCAR pure BNE": ";".join(equilibrium_label(eq) for eq in ccar),
                "Baseline BNE count": len(baseline),
                "CCAR BNE count": len(ccar),
                "No effect on equilibrium set": no_effect,
                "Robust welfare improvement": robust_improvement,
                "Excessive disclosure by stated diagnostic": excessive,
                "Any CCAR gap exceeds worst baseline gap": increased_gap,
                "Multiple CCAR pure BNE": len(ccar) > 1,
                "No CCAR pure BNE": len(ccar) == 0,
                "Baseline welfare min": min(baseline_welfare) if baseline_welfare else "",
                "Baseline welfare max": max(baseline_welfare) if baseline_welfare else "",
                "CCAR welfare min": min(ccar_welfare) if ccar_welfare else "",
                "CCAR welfare max": max(ccar_welfare) if ccar_welfare else "",
                "Full-information first-best welfare": first_best_welfare,
            })
write_csv(TABLE_DIR / "ccar_failure_regions.csv", failure_rows)

diagnostics = [
    "No effect on equilibrium set",
    "Robust welfare improvement",
    "Excessive disclosure by stated diagnostic",
    "Any CCAR gap exceeds worst baseline gap",
    "Multiple CCAR pure BNE",
    "No CCAR pure BNE",
]
for diagnostic in diagnostics:
    print(diagnostic, sum(bool(row[diagnostic]) for row in failure_rows), "of", len(failure_rows))
"""
    ),
    md(
        r"""
## Interpretation and limitations

The baseline identifies congestion-dependent type-contingent disclosure and a gap from a planner who observes realized types. CCAR can alter incentives by reducing access to enhanced non-safety coordination information after Minimum disclosure, but its evaluation depends on the same underlying welfare yardstick as the baseline. Results are computational findings for a small stylized game.

Important unresolved extensions include correlated or interdependent types, richer continuous disclosure, dynamic learning and reputation, heterogeneous congestion exposure, compliance and auditing costs, endogenous congestion, mixed BNE where no pure BNE exists, and an implementability analysis of the full-information benchmark.
"""
    ),
    code(
        r"""
package_names = ["numpy", "matplotlib", "nbformat", "nbclient", "ipykernel"]
metadata_rows = [
    {"item": "python_version", "value": platform.python_version()},
    *[{"item": f"package_{name}", "value": metadata.version(name)} for name in package_names],
    {"item": "actions", "value": str(ACTIONS)},
    {"item": "types", "value": str(TYPES)},
    {"item": "type_probabilities", "value": str(TYPE_PROB)},
    {"item": "congestion", "value": str(CONGESTION)},
    {"item": "benefit_scale_B", "value": BENEFIT_SCALE},
    {"item": "lambda", "value": LAMBDA},
    {"item": "benchmark_alpha_M", "value": ALPHA_M},
    {"item": "table_output_path", "value": str(TABLE_DIR.relative_to(ROOT))},
    {"item": "figure_output_path", "value": str(FIGURE_DIR.relative_to(ROOT))},
]
write_csv(TABLE_DIR / "disclosure_run_metadata.csv", metadata_rows)
print("Reproducibility record")
for row in metadata_rows:
    print(f"{row['item']}: {row['value']}")
"""
    ),
]

notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3"},
    },
)
NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
nbf.write(notebook, NOTEBOOK)
print(f"Wrote {NOTEBOOK}")
