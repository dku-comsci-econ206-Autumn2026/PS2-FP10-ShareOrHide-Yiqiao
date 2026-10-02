"""Build the Week 5 priority-slot allocation notebook from auditable cells."""

from pathlib import Path

import nbformat as nbf

from notebook_bootstrap import BOOTSTRAP_SOURCE


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "02_priority_slot_allocation.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


cells = [
    md(
        r"""
# Week 5 application: allocating a scarce priority-access slot

This notebook studies a **bounded downstream application** of the core project on strategic flight-intent disclosure in congested low-altitude drone traffic:

> strategic flight-intent disclosure $\rightarrow$ traffic information and congestion management $\rightarrow$ residual demand may still exceed capacity $\rightarrow$ allocate a scarce priority-access slot $\rightarrow$ compare FCFS with a second-price auction.

The auction is **not** the main research innovation and is not merged into the Bayesian disclosure game.

## Auction boundary statement

This priority-slot auction represents a short-run downstream allocation problem after corridor scarcity has been identified. It does not model the entire low-altitude traffic-management system. Values are treated as independent private values for tractability, although real missions may involve common or interdependent value components due to shared congestion, weather, and safety conditions.
"""
    ),
    md(
        r"""
## PS2 Week 5 mechanism checklist

| Required element | Operational definition in this notebook |
|---|---|
| **Scarce resource** | One priority-access slot for a congested low-altitude corridor during a fixed short time window; benchmark capacity $K=1$. |
| **Participants** | Eligible non-emergency commercial drone operators. Emergency and public-safety flights receive policy priority outside the payment-based benchmark and are explicitly excluded. |
| **Values/signals** | Private normalized value $v_i=$ avoided delay cost + service value of earlier passage. These units are not labeled dollars. |
| **Information** | In the benchmark, each operator knows its own value; values are independent private values (IPV). FCFS uses request order and the auctioneer observes submitted bids after closing. |
| **Bids/reports** | FCFS receives valid requests; the auction receives sealed bids $b_i$. |
| **Allocation rule** | FCFS assigns the earliest eligible valid request; the $K=1$ Vickrey auction assigns the highest eligible bid. |
| **Payment rule** | FCFS payment is 0. The auction winner pays the second-highest eligible bid. |
| **Stopping rule** | FCFS stops once all $K$ slots are allocated. Auction bidding closes at a fixed deadline, then allocation occurs after all eligible bids are submitted. |
| **Rational benchmark** | In the standard IPV benchmark, $b_i=v_i$ is weakly dominant in a second-price auction. This claim is not extended to common- or interdependent-value settings. |
"""
    ),
    code(
        BOOTSTRAP_SOURCE
        + """

import csv
import importlib.metadata as metadata
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.priority_slot_allocation import (
    allocate_fcfs,
    second_price_auction,
    simulate_bid_noise_stress,
    simulate_truthful_comparison,
)

TABLE_DIR = ROOT / "outputs" / "tables"
FIGURE_DIR = ROOT / "outputs" / "figures"
TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

SEED = 206
STRESS_SEED = 1206
ROUNDS = 10_000
N_BIDDERS = 4
VALUE_LOW, VALUE_HIGH = 0.0, 10.0
NOISE_SIGMAS = (0.0, 0.1, 0.25, 0.5, 1.0)

def write_csv(path, rows):
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

print(f"Repository ready: {REPO_NAME}")
print(f"Tables: {TABLE_DIR.relative_to(ROOT)}")
print(f"Figures: {FIGURE_DIR.relative_to(ROOT)}")
"""
    ),
    md(
        r"""
## Illustrative four-operator benchmark

Normalized private values are A: 8, B: 5, C: 3, D: 2. They are illustrative values, not empirical estimates or dollar amounts.

For FCFS, arrival order is B, C, A, D. With $K=1$, B wins. For the sealed-bid auction, bids are truthful in the IPV benchmark. The payment is a transfer to the traffic authority: it reduces the winner's utility and raises auctioneer revenue by the same amount. In this simplest transfer-neutral welfare convention, money does not disappear, so social welfare equals allocated value rather than allocated value minus revenue.
"""
    ),
    code(
        """
benchmark_values = {"A": 8, "B": 5, "C": 3, "D": 2}
arrival_order = ["B", "C", "A", "D"]

fcfs_benchmark = allocate_fcfs(arrival_order, benchmark_values, capacity=1)
auction_benchmark = second_price_auction(benchmark_values, values=benchmark_values)

benchmark_rows = [
    {
        "mechanism": "FCFS",
        "winner": fcfs_benchmark.winners[0],
        "allocated_value": fcfs_benchmark.allocated_value,
        "maximum_feasible_value": fcfs_benchmark.max_feasible_value,
        "payment": fcfs_benchmark.payment,
        "winner_utility": fcfs_benchmark.winner_utility,
        "auctioneer_revenue": 0.0,
        "allocative_efficiency": fcfs_benchmark.allocative_efficiency,
        "social_welfare_transfer_neutral": fcfs_benchmark.social_welfare,
    },
    {
        "mechanism": "Second-price auction (truthful IPV benchmark)",
        "winner": auction_benchmark.winner,
        "allocated_value": auction_benchmark.allocated_value,
        "maximum_feasible_value": auction_benchmark.highest_feasible_value,
        "payment": auction_benchmark.payment,
        "winner_utility": auction_benchmark.winner_utility,
        "auctioneer_revenue": auction_benchmark.auctioneer_revenue,
        "allocative_efficiency": auction_benchmark.allocative_efficiency,
        "social_welfare_transfer_neutral": auction_benchmark.social_welfare,
    },
]
benchmark_path = TABLE_DIR / "auction_benchmark_example.csv"
write_csv(benchmark_path, benchmark_rows)
for row in benchmark_rows:
    print(row)
print(f"Saved {benchmark_path.relative_to(ROOT)}")
"""
    ),
    md(
        r"""
## Monte Carlo design and efficiency definition

We simulate 10,000 independent rounds with four eligible commercial operators. Values are i.i.d. $\mathrm{Uniform}[0,10]$ normalized private values. In each round, FCFS arrival order is an independent uniformly random permutation, implemented by sorting i.i.d. continuous random arrival keys. The seed is fixed.

For $K=1$, normalized allocative efficiency is

$$\frac{\text{value of allocated winner}}{\text{highest feasible value}}.$$

Truthful second-price bidding under IPV therefore allocates to the highest-value bidder and has efficiency 1 (up to zero-probability numerical edge cases). Revenue is recorded separately and is **not** interpreted as welfare.
"""
    ),
    code(
        """
simulation = simulate_truthful_comparison(
    rounds=ROUNDS,
    n_bidders=N_BIDDERS,
    seed=SEED,
    value_low=VALUE_LOW,
    value_high=VALUE_HIGH,
)

summary_rows = [
    {
        "mechanism": "FCFS",
        "rounds": ROUNDS,
        "seed": SEED,
        "mean_allocated_value": float(np.mean(simulation["fcfs_allocated_value"])),
        "mean_payment_revenue": float(np.mean(simulation["fcfs_payment"])),
        "payment_revenue_sd": float(np.std(simulation["fcfs_payment"], ddof=1)),
        "payment_revenue_median": float(np.median(simulation["fcfs_payment"])),
        "payment_revenue_q95": float(np.quantile(simulation["fcfs_payment"], 0.95)),
        "mean_winner_utility": float(np.mean(simulation["fcfs_allocated_value"])),
        "mean_allocative_efficiency": float(np.mean(simulation["fcfs_efficiency"])),
        "mean_social_welfare_transfer_neutral": float(np.mean(simulation["fcfs_social_welfare"])),
    },
    {
        "mechanism": "Second-price auction (truthful IPV benchmark)",
        "rounds": ROUNDS,
        "seed": SEED,
        "mean_allocated_value": float(np.mean(simulation["second_price_highest_value"])),
        "mean_payment_revenue": float(np.mean(simulation["second_price_revenue"])),
        "payment_revenue_sd": float(np.std(simulation["second_price_revenue"], ddof=1)),
        "payment_revenue_median": float(np.median(simulation["second_price_revenue"])),
        "payment_revenue_q95": float(np.quantile(simulation["second_price_revenue"], 0.95)),
        "mean_winner_utility": float(np.mean(simulation["second_price_winner_utility"])),
        "mean_allocative_efficiency": float(np.mean(simulation["second_price_efficiency"])),
        "mean_social_welfare_transfer_neutral": float(np.mean(simulation["second_price_social_welfare"])),
    },
]
summary_path = TABLE_DIR / "auction_simulation_summary.csv"
write_csv(summary_path, summary_rows)
for row in summary_rows:
    print(row)
print(f"Saved {summary_path.relative_to(ROOT)}")
"""
    ),
    md(
        r"""
## Behavioral / bounded-rationality stress test

The truthful benchmark is $b_i=v_i$. To study misunderstanding of second-price incentives, we add controlled multiplicative bid noise:

$$b_i=\max(0,v_i\epsilon_i), \qquad \epsilon_i\sim\operatorname{LogNormal}(-\sigma^2/2,\sigma).$$

Thus $E[\epsilon_i]=1$. The $\sigma=0$ row is truthful; positive $\sigma$ rows are a **behavioral / bounded-rationality stress test**, not rational equilibrium behavior. Values remain i.i.d. Uniform[0,10], and all results use a fixed seed.
"""
    ),
    code(
        """
stress_rows = simulate_bid_noise_stress(
    rounds=ROUNDS,
    n_bidders=N_BIDDERS,
    seed=STRESS_SEED,
    noise_sigmas=NOISE_SIGMAS,
    value_low=VALUE_LOW,
    value_high=VALUE_HIGH,
)
for row in stress_rows:
    row.update({"rounds": ROUNDS, "seed": STRESS_SEED, "noise_distribution": "LogNormal(-sigma^2/2, sigma)"})

stress_path = TABLE_DIR / "auction_behavioral_stress_test.csv"
write_csv(stress_path, stress_rows)
for row in stress_rows:
    print(row)
print(f"Saved {stress_path.relative_to(ROOT)}")
"""
    ),
    md("## Figures (all generated from the simulation arrays above)"),
    code(
        """
plt.style.use("seaborn-v0_8-whitegrid")
COLORS = ["#4C78A8", "#F58518"]

def save_figure(fig, stem):
    for extension in ("png", "svg"):
        fig.savefig(FIGURE_DIR / f"{stem}.{extension}", dpi=180, bbox_inches="tight")
    plt.close(fig)

# 1. Mean allocative efficiency
fig, ax = plt.subplots(figsize=(6.4, 4.2))
means = [summary_rows[0]["mean_allocative_efficiency"], summary_rows[1]["mean_allocative_efficiency"]]
ax.bar(["FCFS", "Second price\\n(truthful IPV)"], means, color=COLORS)
ax.set_ylim(0, 1.05)
ax.set_ylabel("Mean allocative efficiency")
ax.set_title("FCFS vs second-price allocation")
for index, value in enumerate(means):
    ax.text(index, value + 0.02, f"{value:.3f}", ha="center")
save_figure(fig, "auction_average_efficiency")

# 2. Distribution of FCFS efficiency
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.hist(simulation["fcfs_efficiency"], bins=np.linspace(0, 1, 31), color=COLORS[0], edgecolor="white")
ax.set_xlabel("FCFS allocative efficiency")
ax.set_ylabel("Rounds")
ax.set_title("Distribution of FCFS efficiency")
save_figure(fig, "auction_fcfs_efficiency_distribution")

# 3. Second-price revenue/payment distribution
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.hist(simulation["second_price_revenue"], bins=np.linspace(0, 10, 31), color=COLORS[1], edgecolor="white")
ax.set_xlabel("Payment / auctioneer revenue (normalized units)")
ax.set_ylabel("Rounds")
ax.set_title("Second-price payment distribution")
save_figure(fig, "auction_second_price_revenue_distribution")

# 4. Truthful versus noisy bidding
fig, ax = plt.subplots(figsize=(6.4, 4.2))
sigmas = [row["noise_sigma"] for row in stress_rows]
efficiencies = [row["mean_allocative_efficiency"] for row in stress_rows]
ax.plot(sigmas, efficiencies, color="#54A24B", marker="o", linewidth=2)
ax.set_ylim(0, 1.02)
ax.set_xlabel("Multiplicative lognormal noise sigma")
ax.set_ylabel("Mean allocative efficiency")
ax.set_title("Truthful benchmark vs noisy-bidding stress test")
save_figure(fig, "auction_truthful_vs_noisy_efficiency")

print("Saved four figures in PNG and SVG formats:")
for path in sorted(FIGURE_DIR.glob("auction_*")):
    print(path.relative_to(ROOT))
"""
    ),
    md(
        r"""
## Interpretation and access/distributional limitations

Under the IPV efficiency benchmark, second-price allocation targets the highest reported value more directly than FCFS. That is a narrow allocative result—not a claim that Vickrey is better overall.

The auction may raise ability-to-pay and unequal-access concerns; bids may not accurately represent social urgency; real mission values can be interdependent because congestion, weather, and safety conditions are shared; and monetizing priority access can itself be objectionable. A payment mechanism may also require safeguards, auditability, eligibility rules, and alternative priority classes. Social-choice evaluation is therefore multidimensional.

## How the allocation application connects to the core project

Disclosure affects the quality of congestion prediction and scheduling. Better information may reduce how often residual scarcity occurs, but capacity conflicts can remain. Only then does the priority-slot allocation layer activate. This notebook does **not** endogenize disclosure, prediction, congestion, and allocation in one mathematical model; it conditions on scarcity already having been identified.
"""
    ),
    md("## Reproducibility record"),
    code(
        """
package_names = ["numpy", "matplotlib", "nbformat", "nbclient", "ipykernel"]
metadata_rows = [
    {"item": "python_version", "value": platform.python_version()},
    *[{"item": f"package_{name}", "value": metadata.version(name)} for name in package_names],
    {"item": "truthful_seed", "value": SEED},
    {"item": "stress_seed", "value": STRESS_SEED},
    {"item": "simulation_rounds", "value": ROUNDS},
    {"item": "eligible_bidders_per_round", "value": N_BIDDERS},
    {"item": "capacity_K", "value": 1},
    {"item": "value_distribution", "value": "iid Uniform[0,10] normalized units"},
    {"item": "fcfs_arrival_order", "value": "independent uniformly random permutation"},
    {"item": "stress_noise", "value": "mean-one multiplicative lognormal"},
    {"item": "table_output_path", "value": str(TABLE_DIR.relative_to(ROOT))},
    {"item": "figure_output_path", "value": str(FIGURE_DIR.relative_to(ROOT))},
]
metadata_path = TABLE_DIR / "auction_run_metadata.csv"
write_csv(metadata_path, metadata_rows)
for row in metadata_rows:
    print(f"{row['item']}: {row['value']}")
print(f"Saved {metadata_path.relative_to(ROOT)}")
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
