# Cross-artifact consistency audit

Audit date: 2026-10-15. Canonical sources: `src/disclosure_model.py`, `src/priority_slot_allocation.py`, and `outputs/final/release_manifest.json`.

| Field | Canonical value | Paper | Poster | README | Notebook / HF | Result |
|---|---|---|---|---|---|---|
| Title / team / author | Share or Hide? … / FP10 / Yiqiao Liu | Match | Match | Match | Match | PASS |
| Players / types | 2 operators; L/H confidentiality cost | Match | Match | Match | Match | PASS |
| Actions | Minimum / Partial / Full voluntary commercial detail | Match | Match | Match | Match | PASS |
| Safety boundary | Mandatory/basic safety floor never conditioned by CCAR | Match | Match | Match | Visible app disclosure and tested content | PASS |
| Congestion | Low .3 / Medium .6 / High 1.0 | Match | Match | Match | Match | PASS |
| Information / solution | own type known, rival unknown; pure BNE | Match | Match | Match | Match | PASS |
| Baseline BNE | Low M/M; Medium P/M; High P/P by (L,H) | Match | Diagram/text match | Match | Exported lookup matches root model | PASS |
| Baseline welfare / first best / gap | 0/.639/.639; 2.193/3.139/.946; 6.882/7.385/.503 | Match | Match | Match | Match | PASS |
| CCAR example | Medium αM=.7: P/P, welfare 3.089, gap .050 | Match | Match | Match | Lookup matches model | PASS |
| Robustness | 760 cells; 401/334/18/3/66/0; overlapping | Match | Match | Match | Notebook link/source consistent | PASS |
| First-best boundary | realized types observed; reference may be infeasible | Match | Match | Match | Model exposes computation | PASS |
| Evidence label | stylized computation; no aviation/behavior empirical finding | Match | Match | Match | Visible in live static Space | PASS |
| Allocation boundary | downstream FCFS vs one-slot second price; emergency/public safety excluded | Appendix F | Match | Match | Notebook/HF tests match | PASS |
| Acknowledgments / contributions | solo; Feiyu superseded-topic review recovered and bounded; other named roles bounded; Oct. 12/14 records pending | Match | Match | Linked docs | N/A | PASS with human confirmation |
| Version / tested commit | validated source checkpoint `96a1c3a5276267ff6a039d9a11a3d9c4b2cfce38` | Printed in paper | Printed in poster | Release manifest link | HF deployment SHA separately recorded | PASS |

Open discrepancy: the live Hugging Face Space is deployed from its own commit `84d736708a1ff2226cea3bf16bb11daa730764a1`; `app.js`, `styles.css`, `js/logic.mjs`, and the validated model data were byte-identical to the repository copy during the 2026-10-15 live parity check. Live `index.html` also matched after removing Hugging Face's runtime-injected `window.huggingface` metadata script. The audit correction changes paper/poster/release files, not Space runtime code. Hosted Colab execution and a new end-to-end live click-through still require human verification.
