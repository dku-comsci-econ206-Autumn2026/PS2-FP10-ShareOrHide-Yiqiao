# PS2 FP10 A0 poster content

## Header

**COMSCI / ECON 206 · PS2 Research Symposium · Fall 2026**

**Share or Hide? Strategic Disclosure in Congested Low-Altitude Drone Traffic**

Yiqiao Liu · FP10  
Course instructor: Professor Luyao Zhang

## Key message

> The largest benchmark coordination failure appears at intermediate congestion, where additional disclosure is socially valuable but remains privately unattractive to confidentiality-sensitive operators.

**Stylized benchmark.**

## 01 Question & model

### Research question & verified gap

- **Primary:** When competing drone operators privately differ in confidentiality cost, how does congestion affect strategic disclosure, and when does equilibrium disclosure fall below the full-information first best?
- **Integrated:** How should low-altitude traffic systems structure non-safety information sharing when operators privately value commercial confidentiality but collectively benefit from coordination?
- **Setting:** Commercial drone-delivery operators using capacity-constrained urban low-altitude corridors.
- **Stakeholders:** Commercial operators, traffic-management authority, customers, nearby/public stakeholders, and emergency/public-safety users.
- **Verified gap:** Existing AAM work studies limited-information coordination, privacy-preserving mechanisms, traffic protocols, and auctions. This project studies the narrower case in which disclosure granularity is an endogenous strategic choice under privately known commercial confidentiality costs and congestion-dependent information value.

### Strategic model

- **Static Bayesian game · incomplete information**
- Players: operators A and B.
- Private type: `c_i ∈ {c_L,c_H}`, where `c_L=1`, `c_H=1.6`, and `Pr(L)=Pr(H)=0.5`.
- Public congestion: Low `d=0.3`; Medium `d=0.6`; High `d=1.0`.
- Actions: Minimum, Partial, Full.
- Minimum means mandatory/basic safety information only; it never means withholding legally required or safety-critical information.
- Partial means next sector, coarse ETA, and approximate traffic volume.
- Full means richer route, timing, and trajectory information.
- Payoff: `u_i(a_i,a_j;c_i,d)=dB[1-exp(-λ(x_i+x_j))]-c_i k(a_i)`.
- Benchmark: `B=7.5`, `λ=0.5`, `x(M,P,F)=(0,1,2)`, and `k(M,P,F)=(0,1,2.5)`.
- Solution concept: pure-strategy Bayesian Nash equilibrium.

### Three lenses

- **Game theory:** Private types plus M/P/F disclosure produce a Bayesian equilibrium.
- **Social choice:** BNE welfare is compared with the full-information first best.
- **Mechanism design:** A CCAR incentive rule and downstream priority allocation are tested for robustness.

### Downstream Week 5 allocation application

One commercial priority-access slot (`K=1`) is allocated among eligible non-emergency commercial operators; emergency/public-safety missions remain outside the auction under policy priority. With illustrative normalized values `A/B/C/D=8/5/3/2` and FCFS arrival `B→C→A→D`, FCFS selects B (value 5; 62.5% efficiency), while a truthful second-price benchmark selects A (payment 5; winner utility 3; 100% efficiency). This is a downstream scarcity-allocation application, not the core disclosure mechanism.

## 02 Design & evidence

### Figure 1: evidence chain

Private confidentiality type + public congestion → choose Minimum/Partial/Full → compute pure BNE → compare BNE welfare with the full-information first best → test CCAR incentives → Decision Lab (Solo + Peer Play) → priority-slot allocation → robustness and design implication.

### Figure 2: main results

| Congestion | Low type | High type | Welfare gap |
|---|---|---|---:|
| Low | Minimum | Minimum | 0.639 |
| Medium | Partial | Minimum | **0.946** |
| High | Partial | Partial | 0.503 |

**Largest benchmark welfare gap: Medium congestion.** At high congestion, even the high-confidentiality type voluntarily chooses Partial. At medium congestion, additional disclosure is socially valuable but remains privately unattractive.

### Candidate mechanism: CCAR

Mandatory safety information remains universal; only enhanced non-safety information access changes. At medium congestion, the baseline outcome is `(Partial, Minimum)` by low/high type. Under CCAR with `α_M=0.7`, it becomes `(Partial, Partial)`. Underlying welfare moves from `2.193` to `3.089`, while the gap moves from `0.946` to `0.050`.

> Under the benchmark parameterization, CCAR moves the medium-congestion equilibrium closer to the full-information first best.

### Robustness

The validated search covers 760 parameter cells: 401 show no equilibrium-set effect, 334 show a welfare improvement, 18 trigger the excessive-disclosure diagnostic, 3 show a larger welfare gap, 66 have multiple pure BNE, and 0 have no pure BNE. Categories overlap and are not empirical probabilities. **Mechanism performance is parameter-dependent.**

## 03 Impact & dialogue

### Practical case

Commercial drone-delivery operators share capacity-constrained urban low-altitude corridors. The decision is how much non-safety commercial flight-intent information to share and how to allocate residual commercial priority scarcity. Potential benefits are better coordination, lower delay, and more efficient corridor use. Risks include commercial confidentiality, unequal access, over-disclosure, and misspecified incentives. Before adoption, the mechanism would require pilot calibration, operator confidentiality valuations, latency and reliability evidence, safety review, and distributional/access analysis. Correction routes include an auditable rule, a mandatory safety-information floor, appeal/review, parameter revision, and suspension when diagnostics worsen.

### Testable implication

> In an intermediate-congestion pilot with synthetic or calibrated confidentiality types, conditioning only enhanced non-safety coordination access on Partial/Full disclosure should increase Partial disclosure among confidentiality-sensitive operators relative to the baseline rule.

Qualify or reject this implication if disclosure becomes excessive, the welfare gap rises, access becomes systematically unequal, or operational/privacy costs dominate.

### Interdisciplinary evidence

- **Behavioral science:** The Hugging Face Decision Lab includes Solo Decision, self-reflection, Peer Play, benchmark reveal, CCAR comparison, and an auction exercise. It is an exploratory classroom decision exercise, not representative evidence about real drone operators.
- **Computer science:** The public repository and two runnable Colab notebooks reproduce the BNE/welfare/CCAR results and the FCFS/second-price application.
- **Integration:** The computational model defines the benchmark shown in the behavioral artifact; participant reflection identifies where strategic predictions may require behavioral qualification.

### Limitations and next test

Limitations include two operators, two independent private types, pure strategies, stylized normalized parameters, no empirical calibration, a potentially nonimplementable full-information first best, omitted CCAR implementation cost, an IPV auction benchmark, potentially interdependent real mission values, and an exploratory behavioral demo.

The next discriminating test compares baseline disclosure and CCAR under trusted-partner and competitive framing, then classifies deviations by privacy salience, reciprocity/fairness, or strategic misunderstanding.

**Open design question:** At what congestion and confidentiality conditions should enhanced access become conditional without creating excessive disclosure or unequal access?

**Peer-review status: PARTIAL.** The authentic review concerns a superseded project version; no topic-specific review of the final drone-disclosure project was available before final submission.

## Acknowledgments and AI-use note

Course instructor: Professor Luyao Zhang. No empirical operational dataset was used; numerical inputs are stylized. Software used includes Python, NumPy, Matplotlib, nbclient, and Gradio. Poster layout was adapted from the official COMSCI/ECON 206 PS2 A0 Poster Template.

Research question, model choices, interpretation, and final responsibility are the author's. AI tools assisted implementation, debugging, literature-search support, reproducibility checking, formatting, and drafting/editing.

## Selected references

1. Chin, C., Qin, V., Gopalakrishnan, K., & Balakrishnan, H. (2023). Traffic Management Protocols for Advanced Air Mobility. *Frontiers in Aerospace Engineering, 2*, 1176969. <https://doi.org/10.3389/fpace.2023.1176969>
2. Maheshwari, C., Mendoza, M. G., Tuck, V., Su, P.-Y., Qin, V. L., Seshia, S. A., Balakrishnan, H., & Sastry, S. (2025). Privacy-Preserving Mechanisms for Coordinating Airspace Usage in Advanced Air Mobility. *ACM Journal on Autonomous Transportation Systems, 2*(4), 1–34. <https://doi.org/10.1145/3732290>
3. Raith, M. (1996). A General Model of Information Sharing in Oligopoly. *Journal of Economic Theory, 71*(1), 260–288. <https://doi.org/10.1006/jeth.1996.0117>
4. Harsanyi, J. C. (1967). Games with Incomplete Information Played by Bayesian Players, I: The Basic Model. *Management Science, 14*(3), 159–182. <https://doi.org/10.1287/mnsc.14.3.159>
5. Vickrey, W. (1961). Counterspeculation, Auctions, and Competitive Sealed Tenders. *The Journal of Finance, 16*(1), 8–37. <https://doi.org/10.1111/j.1540-6261.1961.tb02789.x>

## Open materials

- GitHub: <https://github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao>
- Validated computational checkpoint: `ffa4836208a3f647181771646c5639286c0726e6`
- Hugging Face Decision Lab: <https://huggingface.co/spaces/dku-comsci-econ206-2026/ps2-share-or-hide-drone-disclosure>
- Colab 01: <https://colab.research.google.com/github/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/blob/main/notebooks/01_strategic_disclosure_game.ipynb>
- Colab 02: <https://colab.research.google.com/github/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao/blob/main/notebooks/02_priority_slot_allocation.ipynb>
- Validation: 65 passed, 0 failed (27 computational, 6 portability, 17 Gradio behavioral, 10 static Python, 5 static JavaScript).
- Both hosted Colab notebooks were manually confirmed by the student to complete **Run all**.
- Peer-review status: **PARTIAL** — superseded-version review only; no topic-specific review of the final drone-disclosure version was available before final submission.
