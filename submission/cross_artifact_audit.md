# Cross-artifact consistency audit

Audit date: 2026-10-03 (Asia/Shanghai)

Overall result: **PASS**

The tracked CSV outputs are the numerical source of truth. README, both notebooks, paper, poster, and behavioral-artifact records were checked for contradiction at their displayed precision.

| Claim | Validated value | Cross-artifact result |
|---|---:|---|
| Baseline BNE — Low | M/M | PASS |
| Baseline BNE — Medium | P/M | PASS |
| Baseline BNE — High | P/P | PASS |
| Welfare gap — Low | 0.639095 | PASS |
| Welfare gap — Medium | 0.946202 | PASS |
| Welfare gap — High | 0.503429 | PASS |
| CCAR `alpha_M` | 0.7 | PASS |
| Medium CCAR BNE | P/P | PASS |
| Medium CCAR underlying welfare | 3.089085 | PASS |
| Medium CCAR gap | 0.050000 | PASS |
| FCFS winner / efficiency | B / 0.625 | PASS |
| Second-price winner / payment / utility / efficiency | A / 5 / 3 / 1.0 | PASS |
| Monte Carlo FCFS mean efficiency | 0.6223078074284918 | PASS |
| Monte Carlo second-price mean efficiency | 1.0 | PASS |

## Artifact-specific checks

- **README:** all local image and document references resolve; seven SVG assets are present; no `/Users`, `Desktop`, or `file://` path appears. The SVG bundle is 41,266 bytes.
- **Notebook 01:** clean in-memory execution completed all 23 code cells; 8 table outputs and 7 plot outputs rendered; fresh plot hashes equal the saved plot hashes.
- **Notebook 02:** clean in-memory execution completed all 10 code cells; 4 table outputs and 5 plot outputs rendered; fresh plot hashes equal the saved plot hashes.
- **Paper:** 8 pages total; exactly 2 main-paper pages; Author Notes starts on page 3; clean Overleaf build has exact extracted-text parity with the submitted PDF and no unresolved citations.
- **Poster:** one editable slide and one PDF page at 1189 × 841 mm; one native table, native text objects, and three images; the `0.946` medium-gap and CCAR result remain unchanged.
- **Behavioral boundary:** the Decision Lab remains an exploratory classroom artifact and is not represented as population evidence.
- **Model boundary:** the two root model modules are unchanged; this freeze modified only final-facing presentation/audit materials.

## Peer review and stale-content result

Status: **PARTIAL — one authentic review was received for a superseded project version; no topic-specific peer review of the final drone-disclosure version was available before final submission.**

No current-facing README, notebook, poster, or main-paper section contains TBD metadata, the superseded interruption project, old public URLs, or an open-ended current-topic PENDING label. “Stay or Switch?” and memory portability remain only in explicitly labeled Appendix B/D or methodological-development records.
