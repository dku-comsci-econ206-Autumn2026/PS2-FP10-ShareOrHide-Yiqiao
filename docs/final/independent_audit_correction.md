# Independent final-submission audit correction

Audit correction date: 2026-10-15, Asia/Shanghai. Basis: `FP10_Final_Submission_Independent_Audit.md`, verified against local files and fetched `origin/main` before modification.

## Issue-by-issue disposition

| Audit issue | Verification against actual repository | Resolution |
|---|---|---|
| Possible stale four-file archive | **Outdated observation.** The four audited hashes exactly matched the four files on fetched `origin/main`; the Section 02 arrow-clarity work was already merged through PR #7 at `f0f39f93d5643cbc8f1c14fe8ad945bdeaa8f327`. | No false rollback or duplicate arrow edit. All four files were regenerated only because confirmed paper/poster/version content changed in this correction. |
| Canvas text entry | **Confirmed.** It named commit `83717dc...`, linked the retired release branch, said “candidate,” and left generic confirmation pending. | Uses `main` URLs, validated source commit `96a1c3a5276267ff6a039d9a11a3d9c4b2cfce38`, audited-final wording, bounded historical evidence, demo fallback, and exact remaining personal checks. |
| Missing final-week records | **Confirmed in part.** October 12/14 primary records were not recoverable. A genuine 28 September Feiyu Li review existed in tracked project materials. | Restored Feiyu Li's review with exact superseded-topic scope and **Revise** decision; did not fabricate Ed posts, roundtables, current-topic review, Ken exchange, or handwritten records. |
| Stale release metadata | **Confirmed.** Manifest, release-readiness document, paper, poster, and Canvas text had old or pending identifiers. | All final-facing artifacts now use the immutable validated source commit above. Release-readiness now states the actual merged-main and correction-branch status. |
| A4 paper figures too small | **Confirmed visually.** The A0 diagrams had been scaled down to unreadable A4 text. | Replaced the paper placements with dedicated LaTeX-native A4 diagrams and a readable paper teaser. The A0 poster diagrams and geometry were not altered. |
| Nearly blank paper page 7 | **Confirmed.** Only a release-audit paragraph remained. | Condensed the redundant release note; final paper is six A4 pages with the main paper still exactly pages 1–2 and Author Notes beginning page 3. |
| Missing standalone structured abstract | **Confirmed.** Appendix E had only the mapping table. | Added a narrative structured abstract covering background, motivation, application/question, method, results, intellectual merits, and practical impacts; retained the eight-row map. |
| Nobel bibliography gap | **Confirmed.** Claims appeared without official references. | Added official NobelPrize.org 2025 and Royal Swedish Academy 2026 entries and citations. |
| Maheshwari venue wrong in README | **Confirmed.** README named the wrong ACM venue. | Corrected to *ACM Journal on Autonomous Transportation Systems* 2(4), Article 19; DOI unchanged. |
| Incomplete reviewer credits | **Confirmed with evidence boundary.** Feiyu Li was omitted from the final version; Han/Xinrong originals remain unavailable. | Added Feiyu Li with strict superseded-topic scope across paper, poster, and feedback registers. Preserved explicit human-confirmation labels for unrecovered records. |
| No demo outage fallback | **Confirmed.** No current tracked screenshot or recording existed. | Generated and tracked a current static-app screenshot and added its README/Canvas links plus a reproducible capture script. |
| Live Space parity/click-through | Prior source-parity record exists; no new authenticated/manual click-through was available. | Runtime code was not changed. Automated Gradio/static tests pass; fresh human live-flow check remains required. |
| Hosted Colab and native PowerPoint | Not recoverable or automatable as personal account/native-app confirmation. | Kept as explicit manual requirements; no completion was invented. |

## Scientific preservation

No payoff, type, action, congestion, equilibrium, welfare, first-best, CCAR, robustness-grid, allocation, notebook, or deployed-app model code was changed. The benchmark and robustness CSV files remained byte-identical to the tested baseline. The validated results remain:

- Low/Medium/High baseline welfare gaps: `0.639095`, `0.946202`, `0.503429`.
- Medium CCAR example at `alpha_M=0.7`: unique pure BNE `(P,P)`, welfare `3.089085`, gap `0.050000`.
- Robustness grid: 760 cells; 401 no-effect, 334 robust-improvement, 18 excessive-disclosure, 3 larger-gap, 66 multiple-CCAR-BNE, and 0 no-pure-BNE flags; diagnostics overlap.

## Verification summary

- 70 automated model/artifact tests: 38 root + 17 Gradio + 10 static Python + 5 static JavaScript, all passed.
- Paper: TeX Live/BibTeX compile passed; 6 A4 pages; main paper exactly pages 1–2; all pages visually inspected.
- Overleaf ZIP: extracted to a clean temporary directory and independently compiled to the same 6-page A4 structure.
- Poster: one editable A0 landscape slide; first-party package and layout validators reported zero findings/warnings; PPTX and exported PDF/PNG were visually inspected.
- Poster containment: 55,904 changed pixels versus the merged-main poster, zero outside the intended lower-right status and footer regions; Section 02 remained unchanged.
- Final release checker: 27 automated checks passed, 0 failed; 3 manual items remain.

## Final four Canvas files

| File | SHA-256 |
|---|---|
| `submission/final/Final-FP10-ShareOrHide.pdf` | `4009b7eeea35395cc8eae2626e6c3df640d0d81bd8db30cade1fe47ac08666a1` |
| `submission/final/Final-FP10-ShareOrHide-Overleaf-Source.zip` | `4a2f8933ab392f25ad0d73fba88516a375010deeb2224ca4b960c213604bca39` |
| `submission/final/Final-FP10-ShareOrHide-A0-Poster.pptx` | `a74674943ef589690d93f8a3136add833db0d68024ccd92d840a61b3d1a20372` |
| `submission/final/Final-FP10-ShareOrHide-A0-Poster.pdf` | `289fabc9c55c4947bf843745bd9ae59a8d5a28b8feadfedd1c33fde6815e5b02` |

## Human confirmation still required

Yiqiao Liu must confirm the final wording/credits and four upload files; provide any genuine October 12/14, Han Zhang, Xinrong Sun, Ken Rogerson, or separate current-topic symposium records; run both notebooks in hosted Colab; test the live Space flows; open the PPTX in native PowerPoint and check print/QR/link behavior; upload four individual files to Canvas and verify the submitted state.
