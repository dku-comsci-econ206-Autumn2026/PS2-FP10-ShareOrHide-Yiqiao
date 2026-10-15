# FP10 Final Project Initial Audit

Audit date: 2026-10-15 (Asia/Shanghai)  
Audited repository: `PS2-ShareOrHide-Yiqiao`  
Original branch at discovery: `main` tracking `origin/main`  
Original HEAD: `6baa4107e508bcf2b1219fefb7827bdfc587714b`  
Working branch created after discovery: `final/fp10-2026-release`

Status vocabulary: **PASS**, **PARTIAL**, **FAIL**, **NOT VERIFIED**, and **HUMAN CONFIRMATION REQUIRED**. A PASS below records inspected evidence, not an inference from a filename.

## A. Existing project structure

| Area | Status | Evidence and finding |
|---|---|---|
| Root public entry point | PASS | `README.md` describes the three-action Bayesian disclosure model, welfare benchmark, CCAR, robustness grid, downstream allocation exercise, two notebooks, and public Space. |
| Computational model | PASS | `src/disclosure_model.py` and `src/priority_slot_allocation.py` exist with corresponding root tests. |
| Notebooks | PASS | `notebooks/01_strategic_disclosure_game.ipynb` and `notebooks/02_priority_slot_allocation.ipynb` exist and include saved outputs. Fresh execution remains a final-release task. |
| Generated evidence | PASS | `outputs/tables/` contains baseline, first-best, CCAR, robustness, and allocation CSVs. `outputs/figures/` contains raster and SVG figures. |
| Behavioral artifacts | PASS | `hf_space/` contains a Gradio counterpart and tests. `hf_static/` contains the deployed static source, finite validated lookup JSON, and Python/JavaScript tests. |
| PS2 paper | PASS | `paper/` contains LaTeX, bibliography, figures, tables, compiled PDF, and a PS2 source ZIP. |
| PS2 poster | PASS | `poster/PS2-FP10-Yiqiao-A0-Poster.pptx` and `.pdf` exist with validation notes and a tracked preview under `docs/assets/poster/`. |
| PS2 submission package | PASS | Four PS2 course-upload artifacts and audit records exist under `submission/`. |
| Final-project release structure | FAIL | `docs/final/`, `outputs/final/`, `figures/final/`, `paper/final/`, `poster/final-poster.*`, and `submission/final/` were absent at discovery. |

Ignored or untracked material was preserved. At discovery the repository had untracked `othres/`, `submission/Team code and members.docx`, and `submission/共享还是隐藏？无人机交通战略披露研究.png`. No destructive Git operation was used.

## B. Current version and commit

- **PASS** — Git history and remotes were inspected.
- **PASS** — Course repository remote: `https://github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao.git`.
- **PASS** — Personal fork remote: `https://github.com/micL1222/PS2-FP10-ShareOrHide-Yiqiao.git`.
- **PASS** — Original audited HEAD: `6baa4107e508bcf2b1219fefb7827bdfc587714b`.
- **PARTIAL** — The untracked team record names older commit `133641f439268a8b2a640fe554b0ae9b230b336a`; it is historical PS2 metadata, not the final tested release.

## C. Existing verified computational results

The original repository instructions were run without code changes on 2026-10-15:

| Test group | Result |
|---|---:|
| Root computational and notebook-portability tests | 33 passed, 0 failed |
| Gradio behavioral logic | 17 passed, 0 failed |
| Static artifact Python tests | 10 passed, 0 failed |
| Static artifact JavaScript tests | 5 passed, 0 failed |
| Total | **65 passed, 0 failed** |

Independent calls to the model API reproduced the tracked benchmark:

| Congestion | Pure BNE | BNE welfare | First-best welfare | First-best minus BNE |
|---|---|---:|---:|---:|
| Low | A(M,M), B(M,M) | 0.000000 | 0.639095 | 0.639095 |
| Medium | A(P,M), B(P,M) | 2.192883 | 3.139085 | 0.946202 |
| High | A(P,P), B(P,P) | 6.881808 | 7.385238 | 0.503429 |

- **PASS** — The gap definition is `expected_first_best_welfare - expected_equilibrium_welfare` under the model's underlying-welfare convention.
- **PASS** — The solver enumerates all `9 × 9 = 81` type-contingent strategy profiles and does not impose symmetry.
- **PASS** — The benchmark has one pure BNE in each congestion state at tolerance `1e-10`.
- **PASS** — Medium-congestion CCAR with `alpha_M = 0.7` changes the equilibrium to A(P,P), B(P,P); underlying welfare is `3.089085`, so the benchmark gap is `0.050000`.
- **PASS** — The robustness CSV contains 760 grid cells: 2 congestion states × 20 high-type costs × 19 access factors.
- **PASS** — Counts reproduce the README: no equilibrium-set effect 401; robust welfare improvement 334; excessive-disclosure diagnostic 18; any larger gap 3; multiple CCAR pure BNE 66; no CCAR pure BNE 0.
- **PASS** — Categories overlap. Examples: 17 cells are both excessive-disclosure and multiple-equilibrium cells; all 3 larger-gap cells also trigger the excessive-disclosure and multiple-equilibrium diagnostics.
- **PARTIAL** — The existing tests validate main arithmetic and enumeration, but final-release tests still need explicit tolerance sensitivity, belief sensitivity, result-manifest parity, and cross-artifact checks.

The welfare values are stylized normalized sums of the two operators' coordination benefits net of modeled confidentiality costs. They are not monetary estimates, empirical aviation effects, probabilities, observations, or participant outcomes. The full-information first best conditions on realized private types and is a comparison reference rather than an implementable institution.

## D. Existing paper, poster, and demo assets

| Asset | Status | Finding |
|---|---|---|
| PS2 paper PDF and source | PASS | Eight-page PS2 PDF plus source ZIP exist. Main text was documented as two pages, followed by Author Notes and Appendices A–F. Final-project eight-part structure and Appendix G are absent. |
| PS2 poster | PASS | One-slide editable A0 poster and one-page PDF exist; PS2 validation reports 1189 × 841 mm. Final-project template migration and three new required diagrams are absent. |
| Notebook 01 | PASS | Contains model, BNE, welfare, CCAR, sensitivity, and failure-grid material. |
| Notebook 02 | PASS | Contains FCFS and truthful second-price priority-slot comparisons with emergency/public-safety exclusion. |
| Static Space | PASS | Finite lookup export, evidence-boundary language, and no-PII tests exist. |
| Gradio Space | PASS | Same-device scenario logic and lookup/model parity tests exist. Deployment parity with the live Space remains to be checked. |
| Demo fallback | PARTIAL | A Chinese PNG screenshot exists untracked; provenance, date, and parity with the live final version are not yet documented. |

## E. Existing feedback and acknowledgment material

- **PASS** — The repository preserves a named September 28 review by Feiyu Li, explicitly scoped to a superseded AI-memory-portability project.
- **PASS** — The existing paper avoids presenting that review as validation of the drone-disclosure model.
- **PARTIAL** — The current master brief supplies faithful summaries attributed to Han Zhang and Xinrong Sun, but no underlying screenshots, post URLs, or review documents are present in the repository.
- **NOT VERIFIED** — No repository record establishes direct review of FP10 by Professor Kenneth S. (Ken) Rogerson.
- **PARTIAL** — Existing acknowledgments credit Professor Luyao Zhang and software/template support but do not yet contain the full final-project list or accurate contribution descriptions for all required people and institutions.
- **HUMAN CONFIRMATION REQUIRED** — Names, dates, and exact contributions for final-week discussion participants must be confirmed from real records before final submission.

## F. Missing final requirements

| Requirement | Status | Initial finding |
|---|---|---|
| Official final-project requirements archive | PASS | Found at `../final project requirements.zip`; an extracted authoritative copy also exists at `../final project requirements/`. |
| Official final Overleaf template | PASS | Source folder inspected; it requires eight named main parts, a named roadmap subsection, Author Notes, references, and Appendices A–G. |
| Exactly two A4 main pages | FAIL | Existing PS2 source follows the PS2 structure and has not been migrated to the final template. |
| Exactly three closest verified papers | FAIL | Existing references are useful but no exactly-three closest-paper audit exists. |
| Intellectual Merits diagram | FAIL | No final diagram with inherited/adapted/new/evidence-status distinctions exists. |
| Practical Impacts diagram with official SDG icons and target codes | FAIL | No compliant diagram exists. |
| New Future Research Roadmap diagram | FAIL | No compliant economics/CS/behavioral roadmap exists. |
| Appendix G and final-week evidence | FAIL | No Appendix G or structured October 12/14 evidence register exists. |
| Final feedback register | FAIL | No final CSV/Markdown register with the required schema exists. |
| Final release manifest | FAIL | No central final results/release manifest exists. |
| Final validation entry point | FAIL | No `scripts/final_release_check.py` exists. |
| Four exact Canvas filenames | FAIL | Only PS2-named submission artifacts exist. |
| Root README final poster embed and repository PDF link | FAIL | README embeds the PS2 preview and PS2 poster path, not `poster/final-poster.png` and `poster/final-poster.pdf`. |

## G. Conflicts or inconsistencies among artifacts

1. **PARTIAL** — The existing README says hosted Colab `Run all` was confirmed during the PS2 freeze. That is historical human verification and cannot be treated as a new final-release live check.
2. **PARTIAL** — The team DOCX asserts a member confirmation for an older PS2 commit. The final Canvas text must remain pending until Yiqiao Liu reviews the final release.
3. **FAIL** — The paper and poster use the PS2 template and do not contain the final project's required eight-part main paper, Appendix G, three diagrams, or full final acknowledgments.
4. **PASS** — Current numerical values agree across the PS2 README, tables, notebook outputs, paper audit, and poster content at displayed precision.
5. **PARTIAL** — The robustness table reports minimum and maximum welfare across equilibrium sets, whereas brief narrative claims often refer to the unique benchmark equilibrium. Final language must state the selection/set criterion explicitly.
6. **NOT VERIFIED** — Live Hugging Face deployment source has not yet been compared byte-for-byte with the repository's final static files.

## H. Proposed changes and scientific risks

1. Preserve the benchmark model and label all added analyses as diagnostics or separate extensions.
2. Add belief and tolerance sensitivity without changing the validated PS2 benchmark.
3. Generate a single machine-readable release manifest and derive final tables/figures from verified outputs.
4. Narrow novelty to a reproducible congestion-contingent comparison that links endogenous disclosure granularity, incomplete information, welfare gaps, and a candidate access rule, including documented failure regions.
5. Treat CCAR as a modeled access-factor intervention for enhanced non-safety coordination information. Do not claim strategy-proofness, optimality, truthful reporting, or real-world safety benefits.
6. Preserve the downstream allocation exercise as a separate application. It is an FCFS baseline versus a truthful second-price benchmark for one residual commercial priority slot.
7. Migrate validated content into the official final paper and A0 poster templates.
8. Add cross-artifact checks before packaging.

Primary scientific risks are overclaiming novelty relative to transport data-sharing research; presenting a full-information benchmark as feasible; treating grid cells as observations or probabilities; concealing equilibrium multiplicity behind one selected outcome; inferring aviation safety, throughput, or emissions effects from stylized welfare; and implying that CCAR can restrict mandatory safety information.

## I. Requirements needing external verification

- **PASS** — The official assignment and scoring materials were located and inspected.
- **PARTIAL** — Los et al. (2020) has been identified as Johan Los, Frederik Schulte, Matthijs T. J. Spaan, and Rudy R. Negenborn, “The value of information sharing for platform-based collaborative vehicle routing,” *Transportation Research Part E*, 141, 102011, DOI `10.1016/j.tre.2020.102011`. Full closest-paper synthesis remains to be written.
- **PARTIAL** — Official UN target wording and icon-use conditions require final citation and asset provenance.
- **PARTIAL** — The official 2026 Economic Sciences announcement and the official 2025 prize materials require a final documented comparison.
- **NOT VERIFIED** — Live GitHub, Colab, and Hugging Face behavior for the final commit must be checked after final artifacts are generated and pushed.

## J. Requirements needing human confirmation

1. Exact source records for Han Zhang's and Xinrong Sun's comments.
2. Exact names and roles of any additional formal or in-class reviewers.
3. Whether Professor Ken Rogerson had a documented direct exchange about this project, and the exact record if so.
4. October 12 and October 14 Ed posts, duet thread, defense responses, self-challenge, assigned replies, symposium notes, award citation, takeaway sheets, exits, and any contribution email.
5. Accurate descriptions of Tencent Shanghai and Shanghai Science and Technology Museum field-learning contributions.
6. Final author review of the paper, poster, contribution statement, acknowledgments, and Canvas confirmation.
7. Hosted Colab `Run all` and final live Space behavior after release.

No missing historical record will be reconstructed as if it occurred. Missing records will remain explicitly labeled until the author supplies or confirms them.
