# Paper source manifest

This paper is derived strictly from the validated PS2 repository state. No model parameter, payoff function, equilibrium routine, first-best routine, welfare convention, CCAR definition, auction rule, or behavioral flow was changed while creating the package.

## Validated checkpoints

- Computational baseline: `791e12224576e5963fd5672f8f90acdcea5556a0`
- Behavioral artifact: `ea7ce241de34b8d21b036d39157ca974c019bb31`
- Static deployed artifact: `a9c51af0b685003f770cce47d810607823847353`
- Notebook portability: `ffa4836208a3f647181771646c5639286c0726e6`

## Final validation status

- Current final test count: **65 passed, 0 failed** (27 computational, 6 notebook-portability, 17 Gradio behavioral, and 15 static/export checks).
- Both notebooks include a Colab bootstrap that automatically shallow-clones the public repository when needed and reuses it within the session.
- Local and isolated Colab-like portability tests passed.
- The student manually confirmed that both hosted Colab notebooks complete **Run all** successfully; this was manual confirmation, not automated hosted-Colab testing.

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
- `paper/references.bib` contains seven verified primary references, including Harsanyi (1967) for the Bayesian-game foundation.
- `paper/acmart.cls` and `paper/ACM-Reference-Format.bst` are copied unchanged from the instructor-provided PS2 Overleaf template.
- `paper/sections/proposal.tex`, `paper/appendices/supporting.tex`, and `paper/figures/ps2_teaser.tex` implement the official five-section, Author Notes, and Appendix A–F organization.
- `paper/template_compliance_audit.md` records each official requirement as PASS, PENDING, FAIL, or NOT APPLICABLE.

## External literature verification

Bibliographic metadata and claim fit were checked against publisher pages, DOI records, arXiv, and institutional repositories. The contribution statement is a distinction, not an absolute novelty claim.

## Public reproducibility links

- Repository: <https://github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao>
- Colab 01: <https://colab.research.google.com/github/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/blob/main/notebooks/01_strategic_disclosure_game.ipynb>
- Colab 02: <https://colab.research.google.com/github/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/blob/main/notebooks/02_priority_slot_allocation.ipynb>

## Course metadata and unresolved review status

- University email: `yl1081@duke.edu` (verified current-project metadata).
- Symposium session: `Session B`, supported by the peer-review sheet identifying `FP10 | Session B | Yiqiao Liu`.
- The validated A0 poster is `poster/PS2-FP10-Yiqiao-A0-Poster.pptx`.
- One authentic review by Feiyu Li (FP3 member 1), dated 2026-09-28, concerns the superseded AI memory-portability version. It is documented in Appendix D and is not relabeled as review of the final low-altitude drone-disclosure model.
- No topic-specific peer review of the final drone-disclosure version was available before final submission. The superseded-version review is used solely in the methodological-development record.
