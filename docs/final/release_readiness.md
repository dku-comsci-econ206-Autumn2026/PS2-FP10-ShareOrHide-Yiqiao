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

- Dedicated branch: `final/fp10-2026-release`.
- **PASS** — The dedicated branch is pushed to both the course repository (`origin`) and the author fork (`fork`); the canonical verified release tag is `fp10-final-2026-10-15-verified-r2`.
- **BLOCKED BY EXTERNAL CREDENTIALS** — Pull-request creation requires an authenticated GitHub web or CLI session. The prepared PR URL is <https://github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/pull/new/final/fp10-2026-release>.
- **NOT YET PUBLISHED ON DEFAULT BRANCH** — Course `main` remains at `6baa4107e508bcf2b1219fefb7827bdfc587714b`. It shows the earlier `docs/assets/poster/ps2_fp10_poster_preview.png`, not the final `poster/final-poster.png`. A human merge is required.
