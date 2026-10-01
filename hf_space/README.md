---
title: Share or Hide?
emoji: 🛩️
colorFrom: blue
colorTo: yellow
sdk: gradio
sdk_version: 6.29.0
app_file: app.py
pinned: false
---

# Share or Hide?

An exploratory classroom decision exercise accompanying the COMSCI/ECON 206 PS2 project **Strategic Disclosure in Congested Low-Altitude Drone Traffic**.

## Purpose and research question

The Space asks:

> When competing drone operators have privately known commercial-confidentiality costs, how much flight-intent information will they strategically disclose as low-altitude traffic congestion changes, and when does the resulting equilibrium disclosure differ from the socially desirable level?

Participants experience the trade-off before seeing the benchmark, reflect on their decisions, compare a baseline choice with the candidate Congestion-Contingent Access Rule (CCAR), and may optionally try peer play and a downstream priority-slot auction.

## How to use

1. In **Solo Decision**, generate a scenario and choose Minimum, Partial, or Full additional disclosure before seeing the rival or benchmark.
2. Review the baseline reveal, then make a second decision under CCAR.
3. Optionally try the second-price priority-slot exercise.
4. In **Peer Play**, use the same device and pass the screen between two participants. The first player's type and action are hidden before the second choice.
5. Read **Model Results** and **About / Methods** after participating.

An optional integer seed makes scenarios reproducible. Leaving it blank generates a new scenario.

## Evidence boundary

**This Space is an exploratory classroom decision exercise. Participant choices are not a representative sample of drone operators, firms, or the public. They do not establish how real operators would behave, and they do not validate the model's external accuracy.**

The numerical parameters are stylized normalized benchmarks rather than empirically calibrated estimates.

## Model assumptions

- Two commercial operators choose simultaneously among three voluntary disclosure levels.
- Mandatory safety information is always available.
- Each operator privately observes Low or High commercial-confidentiality sensitivity.
- Types are independent with prior probability 0.5 each.
- Congestion is public and takes Low, Medium, or High benchmark values.
- The displayed benchmark is a pure-strategy Bayesian Nash equilibrium.
- The full-information first best assumes a planner observes both realized types; it may not be implementable.
- CCAR affects only enhanced non-safety coordination information.
- The auction is a bounded downstream Week 5 application, not the main research contribution.

The economic modules in `src/` are byte-for-byte copies of the validated computational implementation at checkpoint `791e12224576e5963fd5672f8f90acdcea5556a0`.

## Data and privacy

No accounts, email addresses, names, student IDs, IP-address fields, external APIs, or LLM APIs are used. Choices and free-text reflections remain session-local and are not written to a database or sent elsewhere. No persistent aggregate dataset is claimed.

## Relationship to the computational notebooks

The Space delegates payoffs, pure-BNE searches, welfare, full-information first-best comparisons, CCAR outcomes, and auction allocation to copied versions of the modules used by:

- `notebooks/01_strategic_disclosure_game.ipynb`
- `notebooks/02_priority_slot_allocation.ipynb`

The interface does not maintain a separate payoff table or alternative economic model.

## Limitations

The exercise uses two operators, independent binary private types, three disclosure actions, exogenous congestion, stylized parameters, and pure-strategy analysis. Multiple-equilibrium regions exist outside the benchmark. CCAR implementation, enforcement, and administrative costs are omitted. Real mission values may be interdependent. Classroom responses are exploratory and provide no real-world behavioral validation.

