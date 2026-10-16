"""Recompute the FP10 final-project evidence bundle from canonical model code.

This script does not alter the validated PS2 benchmark. It writes a separate
``outputs/final`` bundle and final-facing data figures with explicit provenance.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    equilibrium_label,
    expected_equilibrium_disclosure,
    expected_equilibrium_welfare,
    expected_first_best_disclosure,
    expected_first_best_welfare,
    find_pure_bne,
)


OUTPUT = ROOT / "outputs" / "final"
FIGURES = ROOT / "figures" / "final"
TOL = 1e-10
BENCHMARK_ALPHA = 0.7
VERIFICATION_DATE = "2026-10-16"


def git_value(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() or "NOT_AVAILABLE"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def benchmark_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, congestion in CONGESTION.items():
        baseline = find_pure_bne(congestion, tolerance=TOL)
        ccar = find_pure_bne(
            congestion, tolerance=TOL, ccar=True, alpha_m=BENCHMARK_ALPHA
        )
        first_best = expected_first_best_welfare(congestion)
        for mechanism, result in (("Baseline", baseline), ("CCAR", ccar)):
            for index, equilibrium in enumerate(result.equilibria, start=1):
                welfare = expected_equilibrium_welfare(
                    equilibrium,
                    congestion,
                    ccar=mechanism == "CCAR",
                    alpha_m=BENCHMARK_ALPHA,
                )
                operator_welfare = expected_equilibrium_welfare(
                    equilibrium,
                    congestion,
                    accounting="operator",
                    ccar=mechanism == "CCAR",
                    alpha_m=BENCHMARK_ALPHA,
                )
                rows.append(
                    {
                        "Congestion": label,
                        "d": congestion,
                        "Mechanism": mechanism,
                        "alpha_M": 1.0 if mechanism == "Baseline" else BENCHMARK_ALPHA,
                        "Equilibrium index": index,
                        "Pure BNE": equilibrium_label(equilibrium),
                        "Pure BNE count": len(result),
                        "Profiles checked": result.profiles_checked,
                        "Underlying welfare": welfare,
                        "Operator utility sum": operator_welfare,
                        "Full-information first-best welfare": first_best,
                        "Welfare gap": first_best - welfare,
                        "Expected disclosure": expected_equilibrium_disclosure(equilibrium),
                    }
                )
    return rows


def robustness_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    high_costs = np.round(np.arange(1.1, 3.0001, 0.1), 1)
    alphas = np.round(np.arange(0.10, 1.0001, 0.05), 2)
    for label in ("Medium", "High"):
        congestion = CONGESTION[label]
        for high_cost in high_costs:
            costs = {"L": 1.0, "H": float(high_cost)}
            baseline = find_pure_bne(congestion, confidentiality_costs=costs)
            baseline_welfare = [
                expected_equilibrium_welfare(eq, congestion, confidentiality_costs=costs)
                for eq in baseline
            ]
            first_best_welfare = expected_first_best_welfare(
                congestion, confidentiality_costs=costs
            )
            first_best_disclosure = expected_first_best_disclosure(
                congestion, confidentiality_costs=costs
            )
            for alpha in alphas:
                ccar = find_pure_bne(
                    congestion,
                    confidentiality_costs=costs,
                    ccar=True,
                    alpha_m=float(alpha),
                )
                ccar_welfare = [
                    expected_equilibrium_welfare(
                        eq,
                        congestion,
                        confidentiality_costs=costs,
                        ccar=True,
                        alpha_m=float(alpha),
                    )
                    for eq in ccar
                ]
                ccar_disclosure = [expected_equilibrium_disclosure(eq) for eq in ccar]
                rows.append(
                    {
                        "Congestion": label,
                        "d": congestion,
                        "c_H": high_cost,
                        "alpha_M": alpha,
                        "Baseline pure BNE": ";".join(
                            equilibrium_label(eq) for eq in baseline
                        ),
                        "CCAR pure BNE": ";".join(equilibrium_label(eq) for eq in ccar),
                        "Baseline BNE count": len(baseline),
                        "CCAR BNE count": len(ccar),
                        "No effect on equilibrium set": set(baseline.equilibria)
                        == set(ccar.equilibria),
                        "Robust welfare improvement": bool(
                            baseline_welfare
                            and ccar_welfare
                            and min(ccar_welfare) > max(baseline_welfare) + TOL
                        ),
                        "Excessive disclosure by stated diagnostic": bool(
                            ccar_disclosure
                            and max(ccar_disclosure) > first_best_disclosure + TOL
                        ),
                        "Any CCAR gap exceeds worst baseline gap": bool(
                            baseline_welfare
                            and ccar_welfare
                            and max(first_best_welfare - value for value in ccar_welfare)
                            > max(first_best_welfare - value for value in baseline_welfare)
                            + TOL
                        ),
                        "Multiple CCAR pure BNE": len(ccar) > 1,
                        "No CCAR pure BNE": len(ccar) == 0,
                        "Baseline welfare min": min(baseline_welfare),
                        "Baseline welfare max": max(baseline_welfare),
                        "CCAR welfare min": min(ccar_welfare) if ccar_welfare else "",
                        "CCAR welfare max": max(ccar_welfare) if ccar_welfare else "",
                        "Full-information first-best welfare": first_best_welfare,
                    }
                )
    return rows


def belief_sensitivity_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for p_low in np.round(np.arange(0.1, 0.9001, 0.1), 1):
        beliefs = {"L": float(p_low), "H": float(1.0 - p_low)}
        for label, congestion in CONGESTION.items():
            for mechanism in ("Baseline", "CCAR"):
                kwargs = {"type_prob": beliefs}
                if mechanism == "CCAR":
                    kwargs.update({"ccar": True, "alpha_m": BENCHMARK_ALPHA})
                result = find_pure_bne(congestion, **kwargs)
                welfare = [
                    expected_equilibrium_welfare(eq, congestion, **kwargs)
                    for eq in result
                ]
                rows.append(
                    {
                        "p_L": p_low,
                        "p_H": 1.0 - p_low,
                        "Congestion": label,
                        "Mechanism": mechanism,
                        "Pure BNE count": len(result),
                        "Pure BNE set": ";".join(
                            equilibrium_label(eq) for eq in result
                        ),
                        "Welfare min": min(welfare) if welfare else "",
                        "Welfare max": max(welfare) if welfare else "",
                    }
                )
    return rows


def tolerance_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for tolerance in (1e-12, 1e-10, 1e-8, 1e-6):
        for label, congestion in CONGESTION.items():
            for mechanism in ("Baseline", "CCAR"):
                kwargs = {"tolerance": tolerance}
                if mechanism == "CCAR":
                    kwargs.update({"ccar": True, "alpha_m": BENCHMARK_ALPHA})
                result = find_pure_bne(congestion, **kwargs)
                rows.append(
                    {
                        "Tolerance": tolerance,
                        "Congestion": label,
                        "Mechanism": mechanism,
                        "Pure BNE count": len(result),
                        "Pure BNE set": ";".join(
                            equilibrium_label(eq) for eq in result
                        ),
                        "Profiles checked": result.profiles_checked,
                    }
                )
    return rows


def make_figures(benchmark: list[dict[str, object]], robustness: list[dict[str, object]]) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 15,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )
    baseline = [row for row in benchmark if row["Mechanism"] == "Baseline"]
    labels = [str(row["Congestion"]) for row in baseline]
    bne = [float(row["Underlying welfare"]) for row in baseline]
    first_best = [float(row["Full-information first-best welfare"]) for row in baseline]
    gaps = [float(row["Welfare gap"]) for row in baseline]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    left = ax.bar(x - width / 2, bne, width, label="Pure BNE", color="#1F4E79")
    right = ax.bar(
        x + width / 2,
        first_best,
        width,
        label="Full-information first best",
        color="#D97706",
        hatch="//",
    )
    ax.bar_label(left, labels=[f"{v:.3f}" for v in bne], padding=3)
    ax.bar_label(right, labels=[f"{v:.3f}" for v in first_best], padding=3)
    for index, gap in enumerate(gaps):
        ax.text(index, max(bne[index], first_best[index]) + 0.55, f"gap {gap:.3f}", ha="center", weight="bold")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Expected welfare, normalized units")
    ax.set_ylim(0, max(first_best) + 1.0)
    ax.set_title("Welfare benchmark by public congestion state", pad=14)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(FIGURES / f"welfare_comparison.{suffix}", dpi=220 if suffix == "png" else None, bbox_inches="tight")
    plt.close(fig)

    make_paper_welfare_figure(benchmark)

    diagnostics = [
        "No effect on equilibrium set",
        "Robust welfare improvement",
        "Excessive disclosure by stated diagnostic",
        "Any CCAR gap exceeds worst baseline gap",
        "Multiple CCAR pure BNE",
        "No CCAR pure BNE",
    ]
    counts = [sum(bool(row[key]) for row in robustness) for key in diagnostics]
    labels_short = [
        "No equilibrium-set effect",
        "Robust welfare improvement",
        "Excessive disclosure",
        "Larger welfare gap",
        "Multiple CCAR BNE",
        "No pure CCAR BNE",
    ]
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    bars = ax.barh(labels_short[::-1], counts[::-1], color=["#374151", "#7C3AED", "#B91C1C", "#EA580C", "#0F766E", "#1F4E79"][::-1])
    ax.bar_label(bars, labels=[str(value) for value in counts[::-1]], padding=4, weight="bold")
    ax.set_xlim(0, 475)
    ax.set_xlabel("Grid cells flagged, out of 760")
    ax.set_title("CCAR robustness diagnostics")
    ax.text(
        0,
        -0.17,
        "Diagnostics overlap. Counts are deterministic grid summaries, not probabilities or independent observations.",
        transform=ax.transAxes,
        fontsize=9,
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(FIGURES / f"ccar_robustness.{suffix}", dpi=220 if suffix == "png" else None, bbox_inches="tight")
    plt.close(fig)


def make_paper_welfare_figure(benchmark: list[dict[str, object]]) -> None:
    """Write the half-page-width A4 welfare chart without touching poster assets."""
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    baseline = [row for row in benchmark if row["Mechanism"] == "Baseline"]
    labels = [str(row["Congestion"]) for row in baseline]
    bne = [float(row["Underlying welfare"]) for row in baseline]
    first_best = [float(row["Full-information first-best welfare"]) for row in baseline]
    gaps = [float(row["Welfare gap"]) for row in baseline]
    x = np.arange(len(labels))
    width = 0.34
    # The main figure is placed at roughly half-page width, so this version
    # uses deliberately larger type and shorter labels.
    fig, ax = plt.subplots(figsize=(6.4, 3.35))
    left = ax.bar(x - width / 2, bne, width, label="Pure BNE", color="#1F4E79")
    right = ax.bar(
        x + width / 2,
        first_best,
        width,
        label="First best",
        color="#D97706",
        hatch="//",
    )
    ax.bar_label(left, labels=[f"{v:.3f}" for v in bne], padding=3, fontsize=13)
    ax.bar_label(right, labels=[f"{v:.3f}" for v in first_best], padding=3, fontsize=13)
    for index, gap in enumerate(gaps):
        ax.text(
            index,
            max(bne[index], first_best[index]) + 0.90,
            f"gap {gap:.3f}",
            ha="center",
            fontsize=13,
            weight="bold",
        )
    ax.set_xticks(x, labels, fontsize=14)
    ax.tick_params(axis="y", labelsize=13)
    ax.set_ylabel("Expected welfare", fontsize=14)
    ax.set_ylim(0, max(first_best) + 1.5)
    ax.set_title("Baseline BNE versus first best", fontsize=16, pad=10)
    ax.legend(frameon=False, ncol=2, loc="upper left", fontsize=13)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    for suffix in ("png", "pdf", "svg"):
        figure_path = FIGURES / f"welfare_comparison_paper.{suffix}"
        fig.savefig(
            figure_path,
            dpi=220 if suffix == "png" else None,
            bbox_inches="tight",
        )
        if suffix == "svg":
            figure_path.write_text(
                "\n".join(line.rstrip() for line in figure_path.read_text(encoding="utf-8").splitlines()) + "\n",
                encoding="utf-8",
            )
    plt.close(fig)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    if "--paper-chart-only" in sys.argv:
        make_paper_welfare_figure(benchmark_rows())
        return
    benchmark = benchmark_rows()
    robustness = robustness_rows()
    belief = belief_sensitivity_rows()
    tolerance = tolerance_rows()

    write_csv(OUTPUT / "benchmark_results.csv", benchmark)
    write_csv(OUTPUT / "robustness_results.csv", robustness)
    write_csv(OUTPUT / "belief_sensitivity.csv", belief)
    write_csv(OUTPUT / "tolerance_sensitivity.csv", tolerance)
    make_figures(benchmark, robustness)

    diagnostic_names = [
        "No effect on equilibrium set",
        "Robust welfare improvement",
        "Excessive disclosure by stated diagnostic",
        "Any CCAR gap exceeds worst baseline gap",
        "Multiple CCAR pure BNE",
        "No CCAR pure BNE",
    ]
    counts = {name: sum(bool(row[name]) for row in robustness) for name in diagnostic_names}
    overlaps = {
        f"{left} AND {right}": sum(bool(row[left]) and bool(row[right]) for row in robustness)
        for left, right in combinations(diagnostic_names, 2)
        if sum(bool(row[left]) and bool(row[right]) for row in robustness)
    }
    experiment_manifest = {
        "schema_version": 1,
        "verification_date": VERIFICATION_DATE,
        "model_version": "fp10-disclosure-v1-preserved",
        "benchmark": {
            "question": "How do private confidentiality costs and public congestion shape voluntary disclosure and welfare?",
            "algorithm": "exhaustive enumeration of all 81 pure type-contingent strategy profiles",
            "random_seed": None,
            "selection_rule": "all pure BNE retained; benchmark states are unique",
            "welfare_gap": "full-information first-best welfare minus underlying BNE welfare",
            "reproduction_command": "python scripts/build_final_evidence.py",
        },
        "robustness": {
            "parameter_cells": len(robustness),
            "grid": {"congestion": ["Medium", "High"], "c_H": [1.1, 3.0, 0.1], "alpha_M": [0.1, 1.0, 0.05]},
            "diagnostic_counts": counts,
            "nonzero_overlaps": overlaps,
            "sampling_interpretation": "none; deterministic parameter grid",
        },
        "belief_sensitivity": {
            "cells": len(belief),
            "p_L_grid": [0.1, 0.9, 0.1],
            "purpose": "bounded sensitivity test, not empirical belief estimation",
        },
        "tolerance_sensitivity": {
            "cells": len(tolerance),
            "tolerances": [1e-12, 1e-10, 1e-8, 1e-6],
        },
        "limitations": [
            "two symmetric operators",
            "independent binary confidentiality types",
            "three discrete voluntary disclosure actions",
            "public exogenous congestion",
            "pure-strategy equilibrium focus",
            "no enforcement, administration, or information-quality costs",
            "full-information first best may be infeasible",
            "no empirical aviation calibration",
        ],
    }
    write_json(OUTPUT / "experiment_manifest.json", experiment_manifest)

    figures = []
    for stem in ("welfare_comparison", "welfare_comparison_paper", "ccar_robustness"):
        for suffix in ("svg", "pdf", "png"):
            path = FIGURES / f"{stem}.{suffix}"
            figures.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                    "source": "scripts/build_final_evidence.py",
                    "evidence_status": "computed stylized simulation",
                }
            )
    write_json(OUTPUT / "figure_metadata.json", {"figures": figures})

    generation_commit = git_value("rev-parse", "HEAD")
    validated_source_commit = os.environ.get("FP10_TESTED_COMMIT", generation_commit)
    release_manifest = {
        "project_title": "Share or Hide? Strategic Disclosure in Congested Low-Altitude Drone Traffic",
        "team": "FP10",
        "author": "Yiqiao Liu",
        "course": "COMSCI/ECON 206 - Computational Microeconomics",
        "term": "Autumn 2026, Session 1",
        "model_version": "fp10-disclosure-v1-preserved",
        "source_commit_at_generation": generation_commit,
        "validated_source_commit": validated_source_commit,
        "tested_commit": validated_source_commit,
        "poster_source_commit": os.environ.get(
            "FP10_POSTER_SOURCE_COMMIT", "96a1c3a5276267ff6a039d9a11a3d9c4b2cfce38"
        ),
        "published_merge_commit": None,
        "git_branch": git_value("branch", "--show-current"),
        "verification_date": VERIFICATION_DATE,
        "parameters": {
            "actions": ACTIONS,
            "types": TYPES,
            "disclosure_levels": DISCLOSURE_LEVELS,
            "privacy_costs": PRIVACY_COSTS,
            "confidentiality_costs": CONFIDENTIALITY_COSTS,
            "type_probabilities": TYPE_PROB,
            "congestion": CONGESTION,
            "benefit_scale": BENEFIT_SCALE,
            "decay_lambda": LAMBDA,
            "ccar_alpha_M": BENCHMARK_ALPHA,
            "equilibrium_tolerance": TOL,
        },
        "benchmark_rows": benchmark,
        "robustness_counts": counts,
        "robustness_categories_overlap": True,
        "notebooks": [
            "notebooks/01_strategic_disclosure_game.ipynb",
            "notebooks/02_priority_slot_allocation.ipynb",
        ],
        "hugging_face_url": "https://huggingface.co/spaces/dku-comsci-econ206-2026/ps2-share-or-hide-drone-disclosure",
        "paper_path": "submission/final/Final-FP10-ShareOrHide.pdf",
        "poster_paths": [
            "poster/final-poster.pptx",
            "poster/final-poster.pdf",
            "poster/final-poster.png",
        ],
        "evidence_status": "stylized computational benchmark; no empirical aviation or behavioral finding",
        "environment": {
            "python": platform.python_version(),
            "numpy": importlib.metadata.version("numpy"),
            "matplotlib": importlib.metadata.version("matplotlib"),
        },
        "execution_contexts": {
            "original_baseline_and_notebook_outputs": {
                "source": "outputs/tables/disclosure_run_metadata.csv and auction_run_metadata.csv",
                "python": "3.13.7",
                "numpy": "2.3.5",
                "matplotlib": "3.10.8",
            },
            "final_evidence_and_figure_generation": {
                "source": "captured by scripts/build_final_evidence.py at generation time",
                "python": platform.python_version(),
                "numpy": importlib.metadata.version("numpy"),
                "matplotlib": importlib.metadata.version("matplotlib"),
            },
            "prior_2026_10_03_test_freeze": {
                "source": "submission/test_report.md",
                "python": "3.13.5",
                "node": "22.22.2",
                "numpy": "NOT_RECORDED",
                "matplotlib": "NOT_RECORDED",
            },
            "final_validation": {
                "source": "docs/final/release_readiness.md",
                "status": "RECORDED_AFTER_FINAL_TEST_RUN",
            },
            "paper_compilation": {
                "source": "clean extracted Overleaf build log",
                "status": "RECORDED_AFTER_FINAL_BUILD",
            },
        },
    }
    write_json(OUTPUT / "release_manifest.json", release_manifest)


if __name__ == "__main__":
    main()
