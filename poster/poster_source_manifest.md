# Poster source manifest

This manifest records the source of every major quantitative claim shown on the poster. No result vector was manually substituted for an available tracked output.

## Template and build provenance

| Item | Source |
|---|---|
| Official base file | Course-provided `COMSCI_ECON206_PS2_A0_Poster_Template.pptx` (external source; not committed) |
| Source-template SHA-256 | `2c0bfad24ded809e845d01fd94b814abc4486d431731e0562b24d7bf8f9c0b58` |
| Slide geometry | Source OOXML `ppt/presentation.xml`: `42804000 × 30276000` EMU = `1189 × 841 mm` |
| Reproducibility checkpoint printed on poster | `ffa4836208a3f647181771646c5639286c0726e6` |
| Final PPTX SHA-256 | `968aea3f705effec1bfe80c2cbb244292717c3586de18351bb71f7fe07848137` |
| Final PDF SHA-256 | `90aeafc1f528ac8f96db1429f03a1bcbe75b60f94702d5d391782f5c0f985ec4` |
| Finalization evidence | Finalizer revision v6 passed package, font, native-table, geometry, first-party import, and overflow checks; temporary receipts were not committed |

## Quantitative claims

| Poster claim | Displayed value | Tracked source | Source fields/rows |
|---|---:|---|---|
| Public congestion levels | `0.3`, `0.6`, `1.0` | `outputs/tables/baseline_bne_summary.csv` | `d`, rows Low/Medium/High |
| Low-congestion BNE | Low type Minimum; high type Minimum | `outputs/tables/baseline_bne_summary.csv` | Low row, operator type actions |
| Medium-congestion BNE | Low type Partial; high type Minimum | `outputs/tables/baseline_bne_summary.csv` | Medium row, operator type actions |
| High-congestion BNE | Low type Partial; high type Partial | `outputs/tables/baseline_bne_summary.csv` | High row, operator type actions |
| Low welfare gap | `0.639` | `outputs/tables/baseline_welfare_gap.csv` | Low row; exact `0.6390946521519896` |
| Medium welfare gap | `0.946` | `outputs/tables/baseline_welfare_gap.csv` | Medium row; exact `0.9462017407996144` |
| High welfare gap | `0.503` | `outputs/tables/baseline_welfare_gap.csv` | High row; exact `0.5034294115088898` |
| Medium baseline welfare | `2.193` | `outputs/tables/baseline_welfare_gap.csv` | Medium `BNE welfare`; exact `2.1928832886574043` |
| Medium CCAR strategy at `α_M=0.7` | `(P,P)` for both operators' low/high strategies | `outputs/tables/ccar_bne_summary.csv` | Medium row, A and B strategy fields |
| Medium CCAR underlying welfare | `3.089` | `outputs/tables/ccar_bne_summary.csv` | Medium `Underlying expected welfare`; exact `3.089085029457019` |
| Medium CCAR residual gap | `0.050` | `outputs/tables/ccar_bne_summary.csv` | `3.1390850294570187 - 3.089085029457019` |
| Robustness cells | `760` | `outputs/tables/ccar_failure_regions.csv` | Data-row count |
| No equilibrium-set effect | `401` | `outputs/tables/ccar_failure_regions.csv` | Sum of `No effect on equilibrium set == True` |
| Welfare improvement | `334` | `outputs/tables/ccar_failure_regions.csv` | Sum of `Robust welfare improvement == True` |
| Excessive-disclosure diagnostic | `18` | `outputs/tables/ccar_failure_regions.csv` | Sum of corresponding Boolean field |
| Larger welfare gap | `3` | `outputs/tables/ccar_failure_regions.csv` | Sum of `Any CCAR gap exceeds worst baseline gap == True` |
| Multiple CCAR pure BNE | `66` | `outputs/tables/ccar_failure_regions.csv` | Sum of corresponding Boolean field |
| No CCAR pure BNE | `0` | `outputs/tables/ccar_failure_regions.csv` | Sum of corresponding Boolean field |
| FCFS winner/value/efficiency | B / `5` / `62.5%` | `outputs/tables/auction_benchmark_example.csv` | FCFS row |
| Second-price winner/payment/utility/efficiency | A / `5` / `3` / `100%` | `outputs/tables/auction_benchmark_example.csv` | Truthful IPV benchmark row |

Robustness categories overlap; the poster explicitly states that they are not empirical probabilities.

## Model parameters and definitions

The printed parameterization and action definitions are sourced from the tracked computational model and its validated notebook exposition:

- `src/disclosure_model.py`
- `notebooks/01_strategic_disclosure_game.ipynb`
- `src/priority_slot_allocation.py`
- `notebooks/02_priority_slot_allocation.ipynb`

No model, parameter, equilibrium, welfare, CCAR, auction, behavioral-artifact, or notebook file was modified for this poster task.

## References

Bibliographic metadata was taken from `paper/references.bib`:

1. Chin et al. (2023), *Traffic Management Protocols for Advanced Air Mobility*, DOI `10.3389/fpace.2023.1176969`.
2. Maheshwari et al. (2025), *Privacy-Preserving Mechanisms for Coordinating Airspace Usage in Advanced Air Mobility*, DOI `10.1145/3732290`.
3. Raith (1996), *A General Model of Information Sharing in Oligopoly*, DOI `10.1006/jeth.1996.0117`.
4. Harsanyi (1967), *Games with Incomplete Information Played by Bayesian Players, I*, DOI `10.1287/mnsc.14.3.159`.
5. Vickrey (1961), *Counterspeculation, Auctions, and Competitive Sealed Tenders*, DOI `10.1111/j.1540-6261.1961.tb02789.x`.

## Open-material links and QR evidence

| Artifact | Exact target | Decode evidence |
|---|---|---|
| GitHub QR | `https://github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao` | Source PNG and `poster/assets/github-qr-pdf-export.png` both decoded exactly |
| Hugging Face QR | `https://huggingface.co/spaces/dku-comsci-econ206-2026/ps2-share-or-hide-drone-disclosure` | Source PNG and `poster/assets/hf-qr-pdf-export.png` both decoded exactly |
| Colab 01 | `https://colab.research.google.com/github/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/blob/main/notebooks/01_strategic_disclosure_game.ipynb` | Editable hyperlink in PPTX; printed link label in Open Materials |
| Colab 02 | `https://colab.research.google.com/github/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/blob/main/notebooks/02_priority_slot_allocation.ipynb` | Editable hyperlink in PPTX; printed link label in Open Materials |

## Test-status provenance

Re-run on 2026-10-03:

| Suite | Passed | Failed |
|---|---:|---:|
| Computational | 27 | 0 |
| Notebook portability | 6 | 0 |
| Gradio behavioral | 17 | 0 |
| Static Python | 10 | 0 |
| Static JavaScript | 5 | 0 |
| **Total** | **65** | **0** |

The statement that both hosted Colab notebooks complete **Run all** is a manual confirmation supplied by the student; it was not newly re-run from the poster build environment.
