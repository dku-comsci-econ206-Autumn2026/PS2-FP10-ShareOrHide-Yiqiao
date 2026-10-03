# Poster validation report

Overall status: **PASS**

The verified university email and Session B metadata are not required by the official visible poster layout, so the poster remains uncluttered and unchanged.

| Requirement | Status | Evidence |
|---|---|---|
| Official template used | PASS | Exact official PPTX imported as the base; source SHA-256 `2c0bfad24ded809e845d01fd94b814abc4486d431731e0562b24d7bf8f9c0b58`; template-fidelity coverage `1.0` |
| A0 dimensions | PASS | PPTX `42804000 × 30276000` EMU; PDF `3370.39 × 2383.94 pt`, identified as A0 (`1189 × 841 mm`) |
| Single slide/page | PASS | PPTX slide count 1; PDF page count 1 |
| Editable PPTX | PASS | Text, headings, panels, callouts, connectors, and BNE table remain native editable objects; only logo and QR codes are images |
| PDF export | PASS | Genuine PDF 1.4 exported with Microsoft PowerPoint; embedded text uses the deck's Calibri family (plus Cambria Math where required), with no substituted font family |
| Header | PASS | Course, symposium, term, DKU logo, project title, author/team, instructor preserved |
| Course instructor | PASS | Professor Luyao Zhang |
| Title | PASS | “Share or Hide? Strategic Disclosure in Congested Low-Altitude Drone Traffic” |
| Author/team | PASS | Yiqiao Liu · FP10 |
| Key message | PASS | Required evidence-grounded sentence shown prominently |
| Stylized-benchmark qualification | PASS | Immediate green “STYLIZED BENCHMARK” callout |
| Research question | PASS | Primary and integrated questions included |
| Verified gap | PASS | Narrow non-absolute literature framing included |
| Strategic model | PASS | Players, types, prior, congestion, actions, safety floor, payoff, parameters, and solution concept included |
| Three lenses | PASS | Game theory, social choice, and mechanism design are analytically distinguished |
| Auction/allocation | PASS | Week 5 resource, policy boundary, FCFS and second-price benchmark displayed |
| Figure 1 | PASS | Editable eight-stage analytical pipeline with correctly directed arrows |
| Figure 2 | PASS | Native editable BNE matrix plus welfare and CCAR callouts |
| BNE values | PASS | M/M; P/M; P/P by low/medium/high congestion, matched to tracked CSV |
| Welfare values | PASS | `0.639`, `0.946`, `0.503`; `0.946` visually dominant |
| CCAR | PASS | Baseline-to-treatment state, `α_M=0.7`, welfare `2.193→3.089`, gap `0.946→0.050`, and exact qualifier shown |
| Robustness | PASS | 760-cell counts shown with overlap/non-probability boundary |
| Practical case | PASS | Commercial delivery corridor case, benefits, risks, evidence needs, and correction route shown |
| Testable implication | PASS | Boxed implication plus qualify/reject conditions |
| Behavioral artifact | PASS | Solo Decision, reflection, Peer Play, reveal, CCAR, and auction included |
| Evidence boundary | PASS | Explicit exploratory-classroom/not-representative qualifier |
| Limitations | PASS | Required modeling, implementation, auction, and behavioral limitations condensed without changing meaning |
| Next test | PASS | Baseline/CCAR × trusted-partner/competitive framing test included |
| Acknowledgments | PASS | Instructor, stylized-input statement, software, and official-template adaptation included |
| References | PASS | Five entries from `paper/references.bib` with DOIs |
| AI-use note | PASS | Authorship/final-responsibility boundary and assistance categories stated transparently |
| GitHub | PASS | Correct link, editable hyperlink, and QR |
| Hugging Face | PASS | Correct link, editable hyperlink, and QR |
| Colab | PASS | Both notebooks represented with editable hyperlinks; third QR omitted to avoid clutter |
| 65-test status | PASS | Fresh re-run: 27 computational + 6 portability + 17 Gradio + 10 static Python + 5 static JavaScript = 65 passed, 0 failed |
| QR decode | PASS | Both source PNGs and both 144-DPI PDF-export crops decoded to exact required targets |
| Old-project contamination | PASS | Required stale-project phrases/links absent from poster-facing materials |
| Visual clipping | PASS | Presentation finalizer found 0 layout findings/warnings; `slides_test.py` reported no overflow; high-resolution PDF inspection found no clipping/overlap/missing glyphs |
| Readability | PASS | Title, headings, key message, BNE matrix, dominant `0.946`, CCAR metrics, and section hierarchy remain legible at A0; detail and references are confined to secondary reading zones |
| University email | PASS | Verified as `yl1081@duke.edu`; not required in the official visible poster layout |
| Symposium session | PASS | Verified as Session B; not required in the official visible poster layout |
| Peer-review status | PASS | `PARTIAL`: authentic superseded-version review only; no topic-specific review of the final drone-disclosure version was available before final submission, and no review outcome was fabricated |
| Open design question | PASS | The unchanged future-facing question is labeled `OPEN DESIGN QUESTION` and is not attributed to a final-version reviewer |

## Rendering and inspection evidence

- Final PPTX package integrity: PASS, 0 findings (finalizer revision v6).
- Exact-template dimensions: PASS.
- Template-fidelity coverage: PASS, `1.0` against the single official reference slide.
- Font policy: PASS, 127 checked text runs, Calibri only.
- Native table requirement: PASS, one editable BNE table.
- Presentation overflow test: PASS, no overflow detected.
- PDF render: `poster/assets/poster-pdf-preview-144dpi.png` at `6740 × 4768` pixels.
- PDF page count: 1.
- QR crops from exported PDF: `poster/assets/github-qr-pdf-export.png` and `poster/assets/hf-qr-pdf-export.png`.

## Old-project contamination scan

The final poster-facing files were checked against all eight prohibited stale-project terms and URLs named in the task specification. Result: **none found**.

## Change-boundary check

The final poster consistency repair relabeled the unchanged future-facing prompt as an open design question and clarified the validated computational checkpoint label. Peer-review status remains `PARTIAL`. No source-model logic, benchmark parameter, computed result, notebook calculation, behavioral-artifact behavior, or public URL changed.
