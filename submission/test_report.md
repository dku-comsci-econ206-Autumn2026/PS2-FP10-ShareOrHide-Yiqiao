# Final verification report

Run date: 2026-10-03 (Asia/Shanghai)

Overall result: **65 passed, 0 failed**

## Automated test suites

| Suite | Passed | Failed |
|---|---:|---:|
| Computational model | 27 | 0 |
| Notebook portability | 6 | 0 |
| Gradio behavioral artifact | 17 | 0 |
| Static Python artifact | 10 | 0 |
| Static JavaScript artifact | 5 | 0 |
| **Total** | **65** | **0** |

The first two groups ran together as 33 Python tests. The behavioral and static Python suites ran as separate 17-test and 10-test groups. The JavaScript suite ran five Node test cases. Test execution used Python 3.13.5 and Node v22.22.2 from already installed local runtimes; no dependency was installed or changed during the freeze.

## Notebook fresh runs

| Notebook | Code cells | Executed | Tables | Plots | Errors | Warnings |
|---|---:|---:|---:|---:|---:|---:|
| `01_strategic_disclosure_game.ipynb` | 23 | 23 | 8 | 7 | 0 | 0 |
| `02_priority_slot_allocation.ipynb` | 10 | 10 | 4 | 5 | 0 | 0 |

Both notebooks were executed from clean in-memory notebook objects. Saved files were not rewritten. Fresh plot hashes exactly matched the stored plot hashes, no local filesystem path appeared in outputs, and the Colab bootstraps remained intact.

## Document and poster checks

- Clean Overleaf-source compile: PASS, 8 pages, exact extracted-text parity with the submitted PDF, no unresolved citations.
- Main-paper length: PASS, exactly 2 pages; Author Notes begins page 3.
- Poster PPTX structural/finalizer checks: PASS, one slide, 0 findings, 0 warnings, one required native table.
- Poster overflow check: PASS.
- Poster PDF export: PASS, one A0 landscape page.
- QR decode from the final exported PDF: PASS for GitHub and Hugging Face.
