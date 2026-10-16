# FP10 last-round correction audit

Audit run: 2026-10-16, Asia/Shanghai. Basis: the current correction brief under `docs/final/`, the current branch contents, official course rubric already retained with the project, clean LaTeX builds, rendered pages, and the established test suites. This is a record of locally verifiable evidence; it does not represent author review, hosted execution, or recovered classroom records.

## Confirmed issues and disposition

| ID | Finding verified in current files | Disposition and evidence |
|---|---|---|
| F01 | Required October 12/14 Ed posts, peer responses, roundtable, exit notes, and some named-feedback primary records are absent from tracked project materials. | Left unclaimed. `docs/final/final_week_evidence.md` and Appendix G identify the exact missing evidence and request author confirmation; no activity or contribution was invented. |
| F02 | Local notebook/test results do not prove hosted Colab execution or human click-through of the live Hugging Face app. | Kept as manual confirmation. Local Gradio/static tests remain separately reported; no hosted or human check is marked passed. |
| M01 | The paper-specific Practical Impacts diagram did not include official UN SDG icons. | Added official Goal 9 and Goal 11 assets to the paper diagram and Overleaf ZIP. Rendered page 6 shows undistorted icons and target labels 9.1 and 11.2. |
| M02 | The three paper-roadmap studies lacked explicit potential-collaborator roles. | Added discipline-level prospective collaborator roles for all three studies. No individual or existing collaboration is asserted. |
| M03 | Roadmap progress criteria were incomplete or implicit. | Each of the Economics, Computer Science, and Behavioral Science studies now labels Question, Method/data, Potential collaborator, Progress criterion, and Milestone. Rendered Figure 4 was visually checked. |
| M04 | Figure 1's caption said CCAR was plotted, although the chart only contained baseline BNE and first-best values. | Rewrote the caption and description to identify exactly those two plotted series and point readers to the separate CCAR result. The figure itself has a dedicated larger-type A4 version. |
| M05 | Release metadata incorrectly presented Python 3.13.5 / NumPy 2.1.3 / Matplotlib 3.10.0 as the figure environment. | Clarified provenance: baseline/notebook evidence records Python 3.13.7, NumPy 2.3.5, Matplotlib 3.10.8; the October 3 freeze separately records Python 3.13.5 and Node 22.22.2 without NumPy/Matplotlib versions. Final validation and TeX Live 2026 are logged separately. |
| M06 | Appendix C claimed a repository reuse license although no root license file exists. | Replaced the claim with a bounded statement: public inspection/reproducibility is available, but no additional project reuse license is asserted; upstream assets and software retain their terms. |
| M07 | SDG 11.2 wording could imply demonstrated public-transport accessibility or safety effects. | Qualified it as an indirect, prospective interpretation. The paper explicitly says passenger access, public-transport accessibility, and field safety were not evaluated. |
| M08 | The paper's half-page welfare graphic used type too small for comfortable A4 reading. | Created a paper-only two-series chart with larger data labels, legend, axes, and short labels. The A0 poster source and assets were not changed. All six paper pages were rendered and visually inspected. |
| M09 | The AI record attributed a GPT-5 model family without retained evidence proving the underlying model identifier. | Changed the record to say the exact model identifier is not independently verified. Also states that Codex rendering is not personal author review. |
| L01 | Prior audit raised concern that poster footer text might be too small. | No current defect was found in the previously validated A0 poster. The poster PDF/PPTX remained byte-identical; no geometry or Section 02 edits were made. Native PowerPoint viewing remains a human check. |
| L02 | Source, packaging, and merged-release version identifiers were conflated in earlier release notes. | Release metadata and readiness notes distinguish the validated source commit, artifact-packaging commit, and published merge commit. The poster retains the source identifier embedded in its unchanged file. |

## Verification performed on resume

- Full source build: `latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex`; bibliography resolved on the final pass, no fatal error, 6 A4 pages.
- Page structure: all eight required main sections and the named Future Research Roadmap fit on pages 1–2; Author Notes begins on page 3; Appendix sections A–G and References remain present.
- Visual inspection: all six pages rendered; no clipped chart, icon, caption, roadmap node, or page break found. Small table-cell hyphenation warnings remain typographic, not content loss.
- Independent ZIP build: extracted the Overleaf source ZIP into a fresh temporary directory and compiled there. Result is 6 A4 pages; extracted PDF text matches the direct project build exactly. PDF bytes differ because the separate builds stamp different build metadata.
- Test suites: 38 root, 17 Gradio, 10 static Python, and 5 Node tests passed (70 total).
- Canonical CSV checksums remain unchanged: `benchmark_results.csv` = `c48142c2b4a974ca872883df7b9158b8f99442788eac59f4fdaf9fe3ec4f3745`; `robustness_results.csv` = `83d01ce0f1e9d2399b939e261ea9321f3ac2f09cdd84c45d5bf4be6ee49ac27d`. Baseline notebook metadata checksums also remain unchanged.

## Remaining human actions

The author must confirm final wording, credits, author order, and the four Canvas uploads; provide any authentic October 12/14 or other missing historical records; run both notebooks in hosted Colab; inspect the live Hugging Face interaction; and open the PPTX in native PowerPoint for fonts, links, QR codes, and print preview. These are not represented as automated passes.

## Release identifiers

Validated source commit: `722211568f1244013071c2d7f126486b4bd259bb`; artifact-packaging commit: `3a0995d069236fe6ac3107f0c83438f530839c9c`; published merge commit: none because the branch is not merged. No commit hash is guessed.
