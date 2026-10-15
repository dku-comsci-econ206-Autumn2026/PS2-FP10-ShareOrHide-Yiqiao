# Final release readiness

Audit date: 2026-10-15, Asia/Shanghai. This file is updated after the final test/commit cycle.

## Verified locally

- **PASS** — Original model preserved: two operators, two private cost types, three disclosure actions, three public congestion states.
- **PASS** — Baseline and CCAR values recomputed from canonical code; robustness categories confirmed overlapping.
- **PASS** — 70 automated tests pass: 38 root, 17 Hugging Face/Gradio, 10 static Python, 5 static JavaScript.
- **PASS** — Both notebooks execute locally from top to bottom. Executed-copy SHA-256: strategic `e86610ee7b0b188cb55ba78a3a7cb3c702dfab3a3fb799d22871ae5e0868c564`; allocation `8b1582eee65d3e257ed8a14dc293fc230abc2deae9cc46cce075cd4af097bdc9`.
- **PASS** — Paper compiles with TeX Live; A4; seven pages total; required main paper is exactly pages 1–2; Author Notes and Appendices A–G follow.
- **PASS** — Clean extracted Overleaf ZIP compiles without repository-local dependencies.
- **PASS** — Poster is one editable slide, 46.811 × 33.1102 inches (1189 × 841 mm nominal A0 landscape), based on the official template; layout validator reports no findings.
- **PASS** — Poster PDF is one A0 landscape page and its PNG preview was rendered from that PDF and visually inspected.
- **PASS** — The Intellectual Merits correction passes DOM geometry validation (11 cards, 9 connectors, zero failures), and a full-poster pixel diff reports exactly zero changed pixels outside the intended diagram rectangle.
- **PASS** — The paper figure, Overleaf figure, editable-poster embedded PNG, stable poster outputs, and four Canvas deliverables are synchronized to the corrected diagram. The clean extracted ZIP still compiles to seven A4 pages.
- **PASS** — The final poster body is globally rebalanced to approximately 26.6% / 46.9% / 26.5% column shares. Section 02's evidence-chain display area is 54.8% larger than the pre-rebalance baseline; the welfare chart and verification evidence remain paired horizontally; Practical Impacts and the roadmap retain even visual weight.
- **PASS** — Global poster pixel QA reports zero changes outside the intentionally rebalanced main-body region, with byte-identical header/key-message and footer regions.
- **PASS** — The Section 02 arrow-clarity audit gives every connector a dedicated whitespace lane (32–60 px across the nine measured separations), reports zero text/card collisions, and finds zero changed pixels outside Section 02; Sections 01 and 03 plus the header and footer are byte-identical to the pre-fix poster.
- **PASS** — Live Hugging Face project page and static runtime returned HTTP 200. API reports public, enabled, RUNNING, SDK `static`, deployment SHA `84d736708a1ff2226cea3bf16bb11daa730764a1`.
- **PASS** — Live Hugging Face `app.js`, `styles.css`, `js/logic.mjs`, and `data/validated_model_data.json` hashes match local `hf_static/` byte-for-byte. Live `index.html` matches after removing Hugging Face's runtime-injected `window.huggingface` metadata script.
- **PASS** — Root README contains the exact required poster preview embed and repository PDF link.

## Manual verification required

- **NEEDS HUMAN CONFIRMATION** — Yiqiao Liu must approve scientific wording, attribution, acknowledgments, author order, and the final four upload files.
- **NEEDS HUMAN CONFIRMATION** — Supply/confirm primary records for October 12/14 activities, Han Zhang and Xinrong Sun feedback dates/wording, the intended Los citation, named class contributors, any Ken Rogerson exchange, and the 28 September symposium record.
- **NEEDS HUMAN CONFIRMATION** — Run both notebooks in hosted Colab and retain success screenshots or links; local execution does not prove hosted execution.
- **NEEDS HUMAN CONFIRMATION** — Open the PPTX in Microsoft PowerPoint and check fonts, QR scanning, hyperlinks, and print preview. LibreOffice PDF export and first-party package validation do not prove native PowerPoint rendering.
- **NEEDS HUMAN CONFIRMATION** — Inspect the final PDFs at 100% and perform the Canvas upload; no upload was attempted.

## External release state

- The original FP10 final-release PR #4 is merged on course `main` at `a33234e`.
- The arrow-clarity branch `fix/fp10-section02-arrow-clarity` continues from the global-rebalance commit `e4ebc6c`. Historical release tags remain unchanged.
- **BLOCKED BY EXTERNAL CREDENTIALS** — Pull-request creation requires an authenticated GitHub web or CLI session. The prepared course-repository PR URL is <https://github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/pull/new/fix/fp10-section02-arrow-clarity>.
- **ARROW-CLARITY RELEASE NOT YET ON DEFAULT BRANCH** — Course `main` contains the earlier final release. Its README uses the correct poster path, but this refined Section 02 preview will not appear there until this branch is merged.
