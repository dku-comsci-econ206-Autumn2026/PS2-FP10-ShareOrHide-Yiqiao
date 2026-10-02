# Paper source manifest

This paper is derived strictly from the validated PS2 repository state. No model parameter, payoff function, equilibrium routine, first-best routine, welfare convention, CCAR definition, auction rule, or behavioral flow was changed while creating the package.

## Validated checkpoints

- Computational baseline: `791e12224576e5963fd5672f8f90acdcea5556a0`
- Behavioral artifact: `ea7ce241de34b8d21b036d39157ca974c019bb31`
- Static deployed artifact: `a9c51af0b685003f770cce47d810607823847353`

## Core computational sources

- `src/disclosure_model.py`: payoff primitives, pure-BNE enumeration, first-best and welfare accounting, and CCAR access rule.
- `src/priority_slot_allocation.py`: FCFS, second-price allocation, seeded benchmark simulation, and noisy-bid stress test.
- `notebooks/01_strategic_disclosure_game.ipynb`: validated disclosure analysis and generated outputs.
- `notebooks/02_priority_slot_allocation.ipynb`: validated downstream allocation analysis and generated outputs.

## Tables used in prose or appendices

- `outputs/tables/baseline_bne_summary.csv`
- `outputs/tables/expected_utility_check.csv`
- `outputs/tables/first_best_by_type.csv`
- `outputs/tables/baseline_welfare_gap.csv`
- `outputs/tables/ccar_bne_summary.csv`
- `outputs/tables/ccar_alpha_sensitivity.csv`
- `outputs/tables/confidentiality_sensitivity.csv`
- `outputs/tables/full_disclosure_sensitivity.csv`
- `outputs/tables/ccar_failure_regions.csv`
- `outputs/tables/auction_benchmark_example.csv`
- `outputs/tables/auction_simulation_summary.csv`
- `outputs/tables/auction_behavioral_stress_test.csv`
- `outputs/tables/disclosure_run_metadata.csv`
- `outputs/tables/auction_run_metadata.csv`

## Behavioral sources

- `hf_space/README.md` and `hf_space/app.py`: locally validated Gradio artifact and documentation.
- `hf_static/README.md`, `hf_static/index.html`, `hf_static/app.js`, and `hf_static/js/logic.mjs`: public static deployment.
- `hf_static/data/validated_model_data.json`: exported finite model results with provenance.

## Paper-generated files

- `paper/scripts/build_paper_assets.py` reads tracked CSVs and model functions to generate `paper/figures/main_results.pdf`, `paper/figures/main_results.png`, and `paper/tables/bne_verification.tex`.
- `paper/tables/literature_comparison.tex` records verified overlap dimensions.
- `paper/references.bib` contains six verified primary references.
- `paper/acmart.cls` and `paper/ACM-Reference-Format.bst` are copied unchanged from the instructor-provided PS2 Overleaf template.

## External literature verification

Bibliographic metadata and claim fit were checked against publisher pages, DOI records, arXiv, and institutional repositories. The contribution statement is a distinction, not an absolute novelty claim.

## Known unresolved course artifacts

- No GitHub remote has been configured, so no GitHub repository URL or public notebook URL is invented.
- The symposium session has not been assigned.
- The A0 poster is outside this requested paper package and has not been supplied.
- No peer review specific to the current low-altitude disclosure project was found; unrelated earlier feedback is not relabeled.
