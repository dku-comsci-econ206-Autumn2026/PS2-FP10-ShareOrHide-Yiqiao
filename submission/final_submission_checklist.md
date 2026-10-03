# Final PS2 submission checklist

Freeze date: 2026-10-03 (Asia/Shanghai)

Overall pre-commit freeze gate: **PASS**

## Repository and scope

- [x] Branch is `final-submission`.
- [x] `origin` is the course repository and `fork` is `mickeystk/PS2-FP10-ShareOrHide-Yiqiao`.
- [x] `src/disclosure_model.py` and `src/priority_slot_allocation.py` are unchanged in this freeze.
- [x] No payoff definition, benchmark parameter, algorithm, welfare rule, CCAR rule, auction rule, seed, or simulation-round count changed.

## Canvas package

- [x] `PS2-FP10-Yiqiao.pdf` is a valid 8-page PDF.
- [x] Main paper occupies exactly pages 1–2; Author Notes begins on page 3.
- [x] Sections 1–5, References, Author Notes, and Appendices A–F are present.
- [x] University email is `yl1081@duke.edu`; symposium assignment is Session B; no TBD metadata remains.
- [x] `PS2-FP10-Yiqiao-Overleaf-Source.zip` extracts cleanly and compiles from a clean directory.
- [x] Clean-build extracted text exactly matches the submitted paper PDF; no unresolved citations were reported.
- [x] The Overleaf ZIP contains the root source, bibliography, sections, appendices, figures, tables, `acmart.cls`, and `ACM-Reference-Format.bst` without cache or Mac metadata.
- [x] `PS2-FP10-Yiqiao-A0-Poster.pptx` contains one editable A0 landscape slide at 1189 × 841 mm.
- [x] `PS2-FP10-Yiqiao-A0-Poster.pdf` contains one A0 landscape page.
- [x] Poster package, font, native-table, geometry, overflow, and visual checks pass.
- [x] Poster status is `PEER REVIEW: PARTIAL`; no current-topic `PENDING` label remains.
- [x] GitHub and Hugging Face QR codes decode to the exact intended URLs.

## Public-facing artifacts

- [x] README hero, artifact buttons, project pipeline, game table, BNE, welfare, CCAR, robustness, auction, three-lens, behavioral-lab, reproducibility, repository-map, and limitations sections are intact.
- [x] All seven repository-relative README SVG assets exist and parse as XML; total asset size is 41,266 bytes.
- [x] README contains no local absolute path or superseded-project contamination.
- [x] Notebook 01 fresh run: 23/23 code cells, 8 rendered tables, 7 plots, 0 errors, 0 warnings.
- [x] Notebook 02 fresh run: 10/10 code cells, 4 rendered tables, 5 plots, 0 errors, 0 warnings.
- [x] Notebook Colab bootstraps remain intact; no local paths or stale figure outputs were found.
- [x] GitHub, both Colab links, and Hugging Face returned HTTP 200 during the freeze audit.

## Evidence and consistency

- [x] Baseline BNE is Low M/M, Medium P/M, High P/P.
- [x] Welfare gaps are 0.639095, 0.946202, and 0.503429.
- [x] Medium CCAR at `alpha_M = 0.7` is P/P with underlying welfare 3.089085 and gap 0.050000.
- [x] FCFS selects B with efficiency 0.625; truthful second price selects A, charges 5, gives winner utility 3, and has efficiency 1.0.
- [x] Monte Carlo mean efficiencies are 0.6223078074284918 for FCFS and 1.0 for truthful second price.
- [x] Full test matrix is 65 passed, 0 failed.
- [x] Current-facing stale-content scan passes. Superseded-project language appears only in explicitly labeled historical/development records.
- [x] Peer-review status is **PARTIAL**, not PASS and not open-ended PENDING.

## Security and release hygiene

- [x] Final source/package scan found no credentials, private keys, API keys, tokens, passwords, or `.env` files.
- [x] Ignored virtual environments, bytecode, test caches, notebook checkpoints, Mac metadata, and temporary extraction/build directories are excluded from the commit.
- [x] SHA-256 hashes for all four Canvas files are recorded in `file_hashes.sha256`.
- [x] No pull request was created or merged during the freeze.

The final commit hash and fork push receipt are recorded in the operator’s final freeze report because those actions necessarily occur after this checklist is staged.
