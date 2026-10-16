# Final release readiness

## Latest acceptance run — 2026-10-16, Asia/Shanghai

This section supersedes the 15 October snapshot below for the current paper, source ZIP, metadata, test, and hash status. Historical poster and audit-containment checks remain applicable because the poster was not changed.

- **Validated source commit:** `722211568f1244013071c2d7f126486b4bd259bb` on `fix/fp10-final-rubric-and-reproducibility`.
- **Artifact-packaging commit:** `3a0995d069236fe6ac3107f0c83438f530839c9c`; it contains the final paper PDF and independently compiled Overleaf ZIP.
- **Published merge commit:** none. GitHub CLI reports no authenticated GitHub session, so no PR was opened or merged. The correction branch is prepared for push/PR when authenticated.
- **Tests on the validated source:** 38 root/model/notebook, 17 Hugging Face/Gradio, 10 static Python, and 5 static JavaScript tests passed; total 70, zero failures. The release validator separately passes 39 automated checks with zero failures and reports 4 human-only checks.
- **Paper:** 6 A4 pages total; required main text is pages 1–2; Author Notes starts page 3; References and Appendices A–G are present. Local compile and clean-extracted Overleaf ZIP compile both pass. Extracted text matches the local build; independent PDF bytes differ due build metadata.
- **Paper visual QA:** all six pages rendered and inspected. Figure 1 contains baseline pure BNE and full-information first best only, with CCAR described separately. Official SDG 9/11 icons are present without distortion; target 11.2 is qualified as indirect/prospective. All three roadmap studies label Question, Method/data, Potential collaborator, Progress criterion, and Milestone.
- **Scientific result preservation:** benchmark CSV SHA-256 `c48142c2b4a974ca872883df7b9158b8f99442788eac59f4fdaf9fe3ec4f3745`; robustness CSV `83d01ce0f1e9d2399b939e261ea9321f3ac2f09cdd84c45d5bf4be6ee49ac27d`; original notebook metadata hashes remain unchanged. The 81-profile, CCAR, and 760-cell results are unchanged.
- **Poster:** still one editable 1189 × 841 mm landscape slide. PPTX and PDF SHA-256 remain `a74674943ef589690d93f8a3136add833db0d68024ccd92d840a61b3d1a20372` and `289fabc9c55c4947bf843745bd9ae59a8d5a28b8feadfedd1c33fde6815e5b02`; Section 02 was not edited. Native PowerPoint viewing remains unverified.
- **Runtime checks:** live Space page/API currently return HTTP 200; API reports public, enabled, static, deployment SHA `84d736708a1ff2226cea3bf16bb11daa730764a1`. `app.js`, `styles.css`, `js/logic.mjs`, and model JSON match local sources byte-for-byte. Live `index.html` differs only by the runtime-injected `window.huggingface` metadata script. Both Colab URLs return HTTP 200, but neither notebook was run in hosted Colab.
- **Current Canvas artifacts:** PDF 610,359 bytes, SHA-256 `b4e650f82984bc4a2d45d93b5e594fbb4c8cc03a14a84de6226e51939fa98e61`; Overleaf ZIP 168,461 bytes, SHA-256 `f537aa1889f282cb325c59ad0c3bd2659b0178bdff47f456a21549eba4600cb0`; poster PPTX 1,664,002 bytes, SHA-256 as above; poster PDF 1,741,611 bytes, SHA-256 as above. `outputs/final/final_release_check.json` is regenerated after packaging.
- **Human actions remaining:** author approval of wording, acknowledgments and files; supply authentic missing October 12/14 feedback/activity records if available; run both notebooks in hosted Colab; manually exercise the live Space; inspect PPTX in PowerPoint; upload and verify the four Canvas files.

**Readiness: CONDITIONALLY READY.** Local scientific, rubric, build, test, and artifact checks pass. Submission should wait for the human confirmations listed above.

## Historical 2026-10-15 readiness snapshot

The following section preserves the earlier independent-audit record; where its source commit or paper-package details differ, the newer 16 October status above controls.

Audit date: 2026-10-15, Asia/Shanghai.

### Historical 2026-10-15 checks (superseded where the section above gives newer status)

## Verified locally at that snapshot

- **PASS** — Original model preserved: two operators, two private cost types, three disclosure actions, three public congestion states.
- **PASS** — Baseline and CCAR values recomputed from canonical code; robustness categories confirmed overlapping.
- **PASS** — 70 automated tests pass: 38 root, 17 Hugging Face/Gradio, 10 static Python, 5 static JavaScript.
- **PASS** — Both notebooks execute locally from top to bottom. Executed-copy SHA-256: strategic `e86610ee7b0b188cb55ba78a3a7cb3c702dfab3a3fb799d22871ae5e0868c564`; allocation `8b1582eee65d3e257ed8a14dc293fc230abc2deae9cc46cce075cd4af097bdc9`.
- **PASS** — Paper compiles with TeX Live; A4; six pages total; required main paper is exactly pages 1–2; Author Notes and Appendices A–G follow. The former page-7 release-audit orphan has been removed.
- **PASS** — Clean extracted Overleaf ZIP compiles without repository-local dependencies.
- **PASS** — Poster is one editable slide, 46.811 × 33.1102 inches (1189 × 841 mm nominal A0 landscape), based on the official template; layout validator reports no findings.
- **PASS** — Poster PDF is one A0 landscape page and its PNG preview was rendered from that PDF and visually inspected.
- **PASS** — The Intellectual Merits correction passes DOM geometry validation (11 cards, 9 connectors, zero failures), and a full-poster pixel diff reports exactly zero changed pixels outside the intended diagram rectangle.
- **PASS** — The A4 paper now uses paper-specific LaTeX-native diagrams with readable body text and clear connector lanes; the A0 poster retains its separately validated large-format diagram. The clean extracted ZIP compiles to six A4 pages.
- **PASS** — The final poster body is globally rebalanced to approximately 26.6% / 46.9% / 26.5% column shares. Section 02's evidence-chain display area is 54.8% larger than the pre-rebalance baseline; the welfare chart and verification evidence remain paired horizontally; Practical Impacts and the roadmap retain even visual weight.
- **PASS** — Global poster pixel QA reports zero changes outside the intentionally rebalanced main-body region, with byte-identical header/key-message and footer regions.
- **PASS** — The archived Section 02 arrow-clarity audit gives every connector a dedicated whitespace lane (32–60 px across the nine measured separations) and zero text/card collisions. In the independent-audit rebuild, the Section 02 asset and geometry remain unchanged.
- **PASS** — Live Hugging Face project page and static runtime returned HTTP 200. API reports public, enabled, RUNNING, SDK `static`, deployment SHA `84d736708a1ff2226cea3bf16bb11daa730764a1`.
- **PASS** — Live Hugging Face `app.js`, `styles.css`, `js/logic.mjs`, and `data/validated_model_data.json` hashes match local `hf_static/` byte-for-byte. Live `index.html` matches after removing Hugging Face's runtime-injected `window.huggingface` metadata script.
- **PASS** — Root README contains the exact required poster preview embed and repository PDF link.
- **PASS** — A stable Behavioral Decision Lab fallback screenshot is tracked at `docs/assets/demo/behavioral-decision-lab-fallback.png` and linked from the README.
- **PASS** — Validated source commit is `96a1c3a5276267ff6a039d9a11a3d9c4b2cfce38`; the manifest, paper, poster, and Canvas text use this immutable content checkpoint.
- **PASS** — Final poster pixel comparison against the merged-main poster found 55,904 changed pixels, all inside the intended lower-right status area or footer; zero changed pixels occurred outside those regions. Section 02 and the A0 scientific layout are unchanged.
- **PASS** — Final release checker: 27 automated artifact/provenance checks passed, 0 failed, with 3 explicitly manual items.

## Historical 2026-10-15 Canvas file hashes

| File | SHA-256 |
|---|---|
| `Final-FP10-ShareOrHide.pdf` | `4009b7eeea35395cc8eae2626e6c3df640d0d81bd8db30cade1fe47ac08666a1` |
| `Final-FP10-ShareOrHide-Overleaf-Source.zip` | `4a2f8933ab392f25ad0d73fba88516a375010deeb2224ca4b960c213604bca39` |
| `Final-FP10-ShareOrHide-A0-Poster.pptx` | `a74674943ef589690d93f8a3136add833db0d68024ccd92d840a61b3d1a20372` |
| `Final-FP10-ShareOrHide-A0-Poster.pdf` | `289fabc9c55c4947bf843745bd9ae59a8d5a28b8feadfedd1c33fde6815e5b02` |

## Manual verification required

- **NEEDS HUMAN CONFIRMATION** — Yiqiao Liu must approve scientific wording, attribution, acknowledgments, author order, and the final four upload files.
- **NEEDS HUMAN CONFIRMATION** — Supply/confirm primary records for October 12/14 activities, Han Zhang and Xinrong Sun feedback dates/wording, the intended Los citation, named class contributors, any Ken Rogerson exchange, and any separate 28 September current-topic symposium record. Feiyu Li's 28 September superseded-topic review is recovered and explicitly bounded.
- **NEEDS HUMAN CONFIRMATION** — Run both notebooks in hosted Colab and retain success screenshots or links; local execution does not prove hosted execution.
- **NEEDS HUMAN CONFIRMATION** — Open the PPTX in Microsoft PowerPoint and check fonts, QR scanning, hyperlinks, and print preview. LibreOffice PDF export and first-party package validation do not prove native PowerPoint rendering.
- **NEEDS HUMAN CONFIRMATION** — Inspect the final PDFs at 100% and perform the Canvas upload; no upload was attempted.

## External release state

- The arrow-clarity work is already merged on course `main` through PR #7 at `f0f39f93d5643cbc8f1c14fe8ad945bdeaa8f327`; the independent audit's contrary observation was outdated.
- This independent-audit correction is on `fix/fp10-independent-audit-corrections`; historical release tags remain unchanged.
- Pull-request creation requires an authenticated GitHub session. Prepared URL: <https://github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/pull/new/fix/fp10-independent-audit-corrections>.
