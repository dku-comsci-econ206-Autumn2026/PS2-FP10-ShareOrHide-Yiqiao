# Share or Hide? Strategic Disclosure in Congested Low-Altitude Drone Traffic

COMSCI/ECON 206 PS2 computational project.

## Research question

When competing drone operators have privately known commercial-confidentiality costs, how much flight-intent information will they strategically disclose as low-altitude traffic congestion changes, and when does equilibrium disclosure differ from the socially desirable level?

## Research gap and scope

The project isolates the interaction of endogenous disclosure granularity, private commercial-confidentiality sensitivity, and congestion-dependent information value. It does not claim to invent privacy-aware traffic management, reciprocal information sharing, or airspace auctions. All parameter values are stylized normalized quantities, not empirical estimates or dollar values.

Mandatory safety information is always available. “Minimum” refers only to withholding additional voluntary commercial detail, never legally required safety information.

## Three-lens structure

1. **Economic:** a static Bayesian game captures strategic voluntary disclosure under incomplete information.
2. **Computational:** exhaustive equilibrium and full-information first-best enumeration, sensitivity analysis, and reproducible output generation expose parameter-dependent regimes.
3. **Behavioral/social-choice:** confidentiality heterogeneity, bounded welfare accounting, access concerns, and noisy auction bidding show why a single efficiency number is not a complete policy ranking.

## Core Bayesian disclosure model

Two operators simultaneously choose Minimum, Partial, or Full voluntary disclosure. Each privately observes a Low or High confidentiality-sensitivity type; congestion is public. The baseline notebook enumerates all 81 pure Bayesian strategy profiles without imposing symmetry, computes every pure BNE, constructs complete-information payoff matrices directly from the utility formula, and compares equilibrium welfare with a planner's full-information first best while preserving ties.

The full-information benchmark assumes the planner observes realized types. It is a comparison benchmark, not an assertion of implementability.

## Social-choice comparison and CCAR

The Congestion-Contingent Access Rule (CCAR) is a candidate mechanism affecting only enhanced non-safety coordination information. At Medium and High congestion, Minimum disclosure receives an access factor `alpha_M`; mandatory safety information remains unconditional.

CCAR equilibrium behavior uses restricted operator utility, but welfare comparisons retain the baseline underlying value of disclosure. This prevents an artificial access penalty from being counted as a social benefit. The analysis reports regions with no effect, welfare improvement, excessive disclosure, a larger welfare gap, multiple pure BNE, and—if found—no pure BNE. Grid transitions are approximate rather than analytical thresholds.

## Week 5 downstream allocation application

The allocation notebook compares FCFS with a single-unit second-price auction after residual corridor scarcity has been identified. Emergency and public-safety flights are handled outside the payment mechanism. **The auction is a bounded downstream application rather than the main research innovation.** It is not merged into the Bayesian disclosure game.

## Behavioral Science Artifact

`hf_space/` contains the self-contained Gradio source for a planned Hugging Face Space. The classroom exercise asks participants to choose disclosure before seeing the rival or theoretical benchmark, compare baseline and CCAR decisions, optionally use same-device peer play, and try the bounded downstream auction. It stores no accounts or durable behavioral dataset and prominently states the evidence boundary.

Hugging Face Space URL: to be added after deployment

Run locally with:

```bash
cd hf_space
python -m pip install -r requirements.txt
python app.py
```

## Notebooks

- `notebooks/01_strategic_disclosure_game.ipynb`: core Bayesian disclosure model, full-information first best, CCAR, sensitivity analysis, failure-region search, tables, and figures.
- `notebooks/02_priority_slot_allocation.ipynb`: FCFS and truthful second-price allocation benchmarks plus noisy-bidding stress tests.

Both notebooks import reusable logic from `src/`; notebook cells do not duplicate the economic mechanisms.

## Reproduction

Python 3.13 is recommended.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

To regenerate notebook sources:

```bash
python scripts/build_disclosure_notebook.py
python scripts/build_priority_slot_notebook.py
```

Execute notebooks from the repository root with Jupyter, `nbclient`, or another clean-kernel runner. Each notebook creates its output directories if needed and records Python/package versions and parameters in a metadata CSV.

## Outputs

- `outputs/tables/`: equilibrium, first-best, welfare, CCAR, robustness, failure-region, auction, and reproducibility tables.
- `outputs/figures/`: PNG and SVG versions of all computed figures.

No output is hard-coded; tables and figures are regenerated from source-model computations.

## Current limitations

The disclosure game has two operators, two independent private types, three discrete disclosure levels, exogenous public congestion, stylized common functional forms, and a pure-strategy focus. The first best assumes type observability. CCAR omits enforcement, administrative, and implementation costs. Future work should examine correlated/interdependent information, mixed equilibria, continuous disclosure, dynamics and reputation, compliance, endogenous congestion, empirical calibration, and institutional feasibility.

The auction uses an independent-private-values benchmark for tractability. Real urgency can include common or interdependent components, and payment-based priority raises ability-to-pay and unequal-access concerns.
