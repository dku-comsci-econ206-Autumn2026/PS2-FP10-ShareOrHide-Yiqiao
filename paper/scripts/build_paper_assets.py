"""Build paper-only figures from validated computational CSV outputs."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


PAPER_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = PAPER_DIR.parent
TABLE_DIR = REPO_DIR / "outputs" / "tables"
FIGURE_DIR = PAPER_DIR / "figures"
PAPER_TABLE_DIR = PAPER_DIR / "tables"
sys.path.insert(0, str(REPO_DIR))

from src.disclosure_model import ACTIONS, CONFIDENTIALITY_COSTS, CONGESTION, expected_utility_action  # noqa: E402


def read_rows(name: str) -> list[dict[str, str]]:
    with (TABLE_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    bne = read_rows("baseline_bne_summary.csv")
    welfare = read_rows("baseline_welfare_gap.csv")
    ccar = read_rows("ccar_bne_summary.csv")

    congestion = [row["Congestion"] for row in bne]
    x = np.arange(len(congestion))
    action_code = {"M": 0, "P": 1, "F": 2}
    low = [action_code[row["Operator A low-type action"]] for row in bne]
    high = [action_code[row["Operator A high-type action"]] for row in bne]

    bne_welfare = np.array([float(row["BNE welfare"]) for row in welfare])
    first_best = np.array(
        [float(row["Full-information first-best welfare"]) for row in welfare]
    )
    ccar_welfare = np.array(
        [float(row["Underlying expected welfare"]) for row in ccar]
    )

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.5,
            "axes.titlesize": 8.5,
            "axes.labelsize": 7.5,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 6.7,
            "pdf.fonttype": 42,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.05), constrained_layout=True)

    ax = axes[0]
    ax.plot(x, low, marker="o", linewidth=2.0, color="#14877D", label="Low confidentiality cost")
    ax.plot(x, high, marker="s", linewidth=2.0, color="#315EFB", label="High confidentiality cost")
    ax.set_xticks(x, congestion)
    ax.set_yticks([0, 1, 2], ["Minimum", "Partial", "Full"])
    ax.set_ylim(-0.22, 2.2)
    ax.set_title("A. Unique pure BNE by type")
    ax.set_xlabel("Public congestion")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(loc="upper left", frameon=False)

    ax = axes[1]
    width = 0.24
    ax.bar(x - width, bne_welfare, width, color="#315EFB", label="Baseline BNE")
    ax.bar(x, ccar_welfare, width, color="#14877D", label="CCAR, $\\alpha_M=0.7$")
    ax.bar(x + width, first_best, width, color="#18324A", label="Full-information first best")
    for index, (baseline, best) in enumerate(zip(bne_welfare, first_best)):
        ax.text(index - width, baseline + 0.16, f"{baseline:.2f}", ha="center", va="bottom", fontsize=6)
        ax.text(index + width, best + 0.16, f"{best:.2f}", ha="center", va="bottom", fontsize=6)
    ax.annotate(
        "gap 0.95 $\\rightarrow$ 0.05",
        xy=(1, ccar_welfare[1]),
        xytext=(0.7, 5.25),
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": "#14877D"},
        color="#14877D",
        fontsize=6.5,
    )
    ax.set_xticks(x, congestion)
    ax.set_ylabel("Expected welfare")
    ax.set_title("B. Welfare and the CCAR benchmark")
    ax.set_ylim(0, 8.3)
    ax.grid(axis="y", alpha=0.22)
    ax.legend(loc="upper left", frameon=False)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / "main_results.pdf", bbox_inches="tight")
    fig.savefig(FIGURE_DIR / "main_results.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    equilibrium_strategy = {"Low": ("M", "M"), "Medium": ("P", "M"), "High": ("P", "P")}
    lines = [
        r"\begin{table*}[t]",
        r"\caption{Interim expected utility of each action against the benchmark equilibrium rival strategy. The rival strategy and chosen action are ordered by own type $(L,H)$.}",
        r"\label{tab:eu}",
        r"\centering",
        r"\small",
        r"\begin{tabular}{@{}llcrrrl@{}}",
        r"\toprule",
        r"Congestion & Own type & Rival strategy & $EU(M)$ & $EU(P)$ & $EU(F)$ & Equilibrium choice \\",
        r"\midrule",
    ]
    for congestion_name, d in CONGESTION.items():
        opponent = equilibrium_strategy[congestion_name]
        for own_type in ("L", "H"):
            values = [
                expected_utility_action(action, own_type, opponent, d)
                for action in ACTIONS
            ]
            best_index = int(np.argmax(values))
            formatted = []
            for index, value in enumerate(values):
                number = f"{value:.3f}"
                formatted.append(rf"\textbf{{{number}}}" if index == best_index else number)
            chosen = equilibrium_strategy[congestion_name][0 if own_type == "L" else 1]
            lines.append(
                f"{congestion_name} & ${own_type}$ & $({opponent[0]},{opponent[1]})$ & "
                + " & ".join(formatted)
                + f" & ${chosen}$ \\\\"
            )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    PAPER_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    (PAPER_TABLE_DIR / "bne_verification.tex").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
