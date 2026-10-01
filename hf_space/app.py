"""Gradio entry point for the PS2 behavioral-science classroom artifact."""

from __future__ import annotations

import gradio as gr

try:  # Package import in repository tests.
    from .app_logic import (
        ACTION_LABELS,
        EVIDENCE_BOUNDARY,
        MOTIVATION_OPTIONS,
        auction_results_markdown,
        begin_peer_ccar,
        computational_results_markdown,
        format_auction_outcome,
        format_baseline_reveal,
        format_ccar_reveal,
        format_peer_private_view,
        format_peer_reveal,
        format_solo_scenario,
        generate_auction_scenario,
        generate_peer_scenario,
        generate_solo_scenario,
        peer_round_reveal,
        submit_auction_bid,
        submit_baseline_decision,
        submit_ccar_decision,
        submit_peer_choice,
    )
except ImportError:  # ``cd hf_space && python app.py``.
    from app_logic import (
        ACTION_LABELS,
        EVIDENCE_BOUNDARY,
        MOTIVATION_OPTIONS,
        auction_results_markdown,
        begin_peer_ccar,
        computational_results_markdown,
        format_auction_outcome,
        format_baseline_reveal,
        format_ccar_reveal,
        format_peer_private_view,
        format_peer_reveal,
        format_solo_scenario,
        generate_auction_scenario,
        generate_peer_scenario,
        generate_solo_scenario,
        peer_round_reveal,
        submit_auction_bid,
        submit_baseline_decision,
        submit_ccar_decision,
        submit_peer_choice,
    )


RESEARCH_QUESTION = (
    "When competing drone operators have privately known commercial-confidentiality "
    "costs, how much flight-intent information will they strategically disclose as "
    "low-altitude traffic congestion changes, and when does the resulting equilibrium "
    "disclosure differ from the socially desirable level?"
)

ACTION_DESCRIPTIONS = """
| Choice | What it means |
|---|---|
| **Minimum disclosure** | Provide only required/basic traffic information. No additional commercially sensitive flight-intent detail. Mandatory safety information is always available. |
| **Partial disclosure** | Share limited additional information such as next sector, coarse ETA, and approximate traffic volume. |
| **Full disclosure** | Share richer route and timing information, providing more coordination detail but greater commercial exposure. |
"""

CSS = """
.gradio-container { max-width: 1120px !important; }
.hero { border-left: 5px solid #315f72; padding: 0.8rem 1.1rem; background: #f4f8fa; }
.evidence { border: 1px solid #a96b35; background: #fff8ef; padding: 0.8rem 1rem; border-radius: 8px; }
.decision-card { border: 1px solid #d5dde2; border-radius: 10px; padding: 0.8rem; }
.pass-screen { border: 2px dashed #315f72; padding: 1rem; text-align: center; }
"""


def _new_solo(seed):
    state = generate_solo_scenario(seed)
    return (
        state,
        gr.Markdown(value=format_solo_scenario(state), visible=True),
        gr.Column(visible=True),
        None,
        [],
        "",
        gr.Markdown(value="", visible=False),
        gr.Column(visible=False),
        None,
        [],
        "",
        gr.Markdown(value="", visible=False),
        gr.Column(visible=False),
        gr.Column(visible=False),
    )


def _baseline_submit(state, choice, motivations, reflection):
    updated, reveal = submit_baseline_decision(state, choice, motivations, reflection)
    return (
        updated,
        gr.Markdown(value=format_baseline_reveal(updated, reveal), visible=True),
        gr.Column(visible=True),
    )


def _ccar_submit(state, choice, motivations, reflection):
    updated, reveal = submit_ccar_decision(state, choice, motivations, reflection)
    return (
        updated,
        gr.Markdown(value=format_ccar_reveal(updated, reveal), visible=True),
        gr.Column(visible=True),
        gr.Column(visible=True),
    )


def _new_auction(seed, setting):
    state = generate_auction_scenario(seed, setting)
    value = state["values"]["Participant"]
    return (
        state,
        gr.Markdown(
            value=(
                f"### Your private priority value: **{value:.0f} normalized units**\n\n"
                "Submit a sealed bid. Rival bids remain hidden until submission."
            ),
            visible=True,
        ),
        gr.Column(visible=True),
        gr.Markdown(value="", visible=False),
    )


def _auction_submit(state, bid):
    updated, outcome = submit_auction_bid(state, bid)
    return updated, gr.Markdown(value=format_auction_outcome(outcome), visible=True)


def _new_peer(seed):
    state = generate_peer_scenario(seed)
    return (
        state,
        gr.Markdown(value=format_peer_private_view(state), visible=True),
        gr.Column(visible=True),
        gr.Column(visible=False),
        gr.Column(visible=False),
        gr.Markdown(value="", visible=False),
        gr.Button(visible=False),
        gr.Column(visible=False),
    )


def _peer_a_submit(state, choice, reflection):
    updated = submit_peer_choice(state, choice, reflection)
    return (
        updated,
        gr.Column(visible=False),
        gr.Column(visible=True),
        gr.Markdown(
            value=(
                "### Pass the screen\nOperator A's private type and choice are hidden. "
                "Hand the device to Operator B, then continue."
            ),
            visible=True,
            elem_classes=["pass-screen"],
        ),
    )


def _show_peer_b(state):
    return (
        gr.Markdown(value=format_peer_private_view(state), visible=True),
        gr.Column(visible=True),
        gr.Column(visible=False),
    )


def _peer_b_submit(state, choice, reflection):
    updated = submit_peer_choice(state, choice, reflection)
    ccar = updated["phase"] == "ccar_reveal"
    reveal = peer_round_reveal(updated, ccar=ccar)
    return (
        updated,
        gr.Column(visible=False),
        gr.Markdown(value=format_peer_reveal(reveal), visible=True),
        gr.Button("Begin peer CCAR round", visible=not ccar),
        gr.Column(visible=ccar),
    )


def _begin_peer_ccar(state):
    updated = begin_peer_ccar(state)
    return (
        updated,
        gr.Markdown(value=format_peer_private_view(updated), visible=True),
        gr.Column(visible=True),
        None,
        "",
        gr.Button(visible=False),
    )


def build_app() -> gr.Blocks:
    """Construct the self-contained classroom interface."""
    with gr.Blocks(title="Share or Hide?") as demo:
        gr.Markdown(
            f"""
<div class="hero">

# Share or Hide?
### Strategic Disclosure in Congested Low-Altitude Drone Traffic

**Research question:** {RESEARCH_QUESTION}

In plain language: when sharing more can improve traffic coordination but reveal business-sensitive
patterns, what will competitors choose under uncertainty—and how does that compare with the social benchmark?

</div>
"""
        )
        gr.Markdown(f'<div class="evidence">{EVIDENCE_BOUNDARY}</div>')

        with gr.Tabs():
            with gr.Tab("Solo Decision"):
                gr.Markdown(
                    """
### Your role
You are one of two competing commercial drone operators using the same congested low-altitude traffic network.

More flight-intent disclosure may help coordination, but detailed route and timing information can reveal commercially sensitive operating patterns. You will choose before seeing the rival or theoretical benchmark.
"""
                )
                solo_state = gr.State(None)
                auction_state = gr.State(None)
                with gr.Row():
                    solo_seed = gr.Number(
                        label="Optional demo seed",
                        precision=0,
                        value=None,
                        info="Leave blank for a new random scenario; reuse a seed to reproduce one.",
                    )
                    solo_start = gr.Button("Start decision", variant="primary")
                    solo_reset = gr.Button("Generate new scenario")
                solo_scenario = gr.Markdown(visible=False, elem_classes=["decision-card"])

                with gr.Column(visible=False, elem_classes=["decision-card"]) as baseline_panel:
                    gr.Markdown("## Round 1 — Baseline decision\n" + ACTION_DESCRIPTIONS)
                    baseline_choice = gr.Radio(
                        choices=list(ACTION_LABELS),
                        label="How much additional flight-intent information would you voluntarily disclose?",
                    )
                    baseline_motivations = gr.CheckboxGroup(
                        choices=list(MOTIVATION_OPTIONS),
                        label="What motivated your choice? Select one or more.",
                    )
                    baseline_reflection = gr.Textbox(
                        label="Why did you choose this disclosure level? (optional)",
                        lines=2,
                        max_lines=4,
                    )
                    baseline_submit = gr.Button("Submit baseline decision", variant="primary")
                baseline_reveal = gr.Markdown(visible=False, elem_classes=["decision-card"])

                with gr.Column(visible=False, elem_classes=["decision-card"]) as ccar_panel:
                    gr.Markdown(
                        """
## Round 2 — Congestion-Contingent Access Rule (CCAR)
Mandatory safety information remains available to every operator. CCAR affects only enhanced non-safety coordination information, such as high-resolution forecasts or enhanced rerouting support.

At Low congestion there is no restriction. At Medium and High congestion, Minimum disclosure receives `alpha_M = 0.7`; Partial and Full receive `alpha = 1`.
"""
                    )
                    ccar_choice = gr.Radio(
                        choices=list(ACTION_LABELS),
                        label="Under this rule, how much information would you disclose?",
                    )
                    ccar_motivations = gr.CheckboxGroup(
                        choices=list(MOTIVATION_OPTIONS),
                        label="What motivated your CCAR choice?",
                    )
                    ccar_reflection = gr.Textbox(
                        label="Why did CCAR change—or not change—your choice? (optional)",
                        lines=2,
                        max_lines=4,
                    )
                    ccar_submit = gr.Button("Submit CCAR decision", variant="primary")
                ccar_reveal = gr.Markdown(visible=False, elem_classes=["decision-card"])

                with gr.Column(visible=False) as auction_panel:
                    gr.Markdown(
                        """
## Optional downstream application — one priority-access slot
Even with better traffic information, residual capacity scarcity may remain. This stage allocates one non-emergency commercial slot. Emergency/public-safety flights are outside the auction. This is the Week 5 application, not the main research contribution.
"""
                    )
                    with gr.Row():
                        auction_setting = gr.Dropdown(
                            choices=["Truthful benchmark", "Noisy-bidding stress test"],
                            value="Truthful benchmark",
                            label="Rival bidding setting",
                        )
                        auction_start = gr.Button("Try priority-slot allocation")
                    auction_private_value = gr.Markdown(visible=False)
                    with gr.Column(visible=False) as auction_bid_panel:
                        auction_bid = gr.Number(label="Your sealed bid", minimum=0)
                        auction_submit = gr.Button("Submit bid", variant="primary")
                    auction_result = gr.Markdown(visible=False, elem_classes=["decision-card"])

                with gr.Column(visible=False) as solo_final_reflection:
                    gr.Markdown("## Final reflection — responses stay in this browser session")
                    gr.Textbox(label="What mattered most in your decision?", lines=2)
                    gr.Textbox(label="Did the theoretical benchmark change how you view your original choice?", lines=2)
                    gr.Textbox(label="Would you choose differently with a trusted partner rather than a competitor?", lines=2)
                    gr.Textbox(label="If you tried the auction, did you bid differently from your value? Why?", lines=2)
                    gr.Markdown("These reflections are exploratory and are not automatically interpreted as scientific evidence.")

                start_outputs = [
                    solo_state,
                    solo_scenario,
                    baseline_panel,
                    baseline_choice,
                    baseline_motivations,
                    baseline_reflection,
                    baseline_reveal,
                    ccar_panel,
                    ccar_choice,
                    ccar_motivations,
                    ccar_reflection,
                    ccar_reveal,
                    auction_panel,
                    solo_final_reflection,
                ]
                solo_start.click(_new_solo, solo_seed, start_outputs, api_visibility="private")
                solo_reset.click(_new_solo, solo_seed, start_outputs, api_visibility="private")
                baseline_submit.click(
                    _baseline_submit,
                    [solo_state, baseline_choice, baseline_motivations, baseline_reflection],
                    [solo_state, baseline_reveal, ccar_panel],
                    api_visibility="private",
                )
                ccar_submit.click(
                    _ccar_submit,
                    [solo_state, ccar_choice, ccar_motivations, ccar_reflection],
                    [solo_state, ccar_reveal, auction_panel, solo_final_reflection],
                    api_visibility="private",
                )
                auction_start.click(
                    _new_auction,
                    [solo_seed, auction_setting],
                    [auction_state, auction_private_value, auction_bid_panel, auction_result],
                    api_visibility="private",
                )
                auction_submit.click(
                    _auction_submit,
                    [auction_state, auction_bid],
                    [auction_state, auction_result],
                    api_visibility="private",
                )

            with gr.Tab("Peer Play"):
                gr.Markdown(
                    """
## Same-device pass-the-screen mode
Two participants become Operator A and Operator B. Each sees only their own private type before choosing. No accounts or database are used.
"""
                )
                peer_state = gr.State(None)
                with gr.Row():
                    peer_seed = gr.Number(label="Optional demo seed", precision=0, value=None)
                    peer_start = gr.Button("Start Peer Play", variant="primary")
                peer_prompt = gr.Markdown(visible=False, elem_classes=["decision-card"])
                with gr.Column(visible=False, elem_classes=["decision-card"]) as peer_a_panel:
                    peer_a_choice = gr.Radio(choices=list(ACTION_LABELS), label="Operator A choice")
                    peer_a_reflection = gr.Textbox(label="What mattered most? (optional)", lines=2)
                    peer_a_submit = gr.Button("Lock A's choice and hide it", variant="primary")
                with gr.Column(visible=False, elem_classes=["decision-card"]) as peer_b_panel:
                    peer_b_choice = gr.Radio(choices=list(ACTION_LABELS), label="Operator B choice")
                    peer_b_reflection = gr.Textbox(label="What mattered most? (optional)", lines=2)
                    peer_b_submit = gr.Button("Lock B's choice and reveal round", variant="primary")
                with gr.Column(visible=False) as peer_pass_panel:
                    peer_pass_message = gr.Markdown(elem_classes=["pass-screen"])
                    peer_show_b = gr.Button("Operator B: show my private prompt", variant="primary")
                peer_reveal = gr.Markdown(visible=False, elem_classes=["decision-card"])
                peer_begin_ccar = gr.Button("Begin peer CCAR round", visible=False)
                with gr.Column(visible=False) as peer_final_reflection:
                    gr.Markdown("## Peer reflection")
                    gr.Textbox(label="Did the benchmark change how you view the choices?", lines=2)
                    gr.Textbox(label="Did CCAR change willingness to disclose? Why?", lines=2)
                    gr.Textbox(label="Would trust or repeated interaction change the result?", lines=2)
                    gr.Markdown("Responses remain session-local and are not treated as scientific evidence.")

                peer_start.click(
                    _new_peer,
                    peer_seed,
                    [peer_state, peer_prompt, peer_a_panel, peer_b_panel, peer_pass_panel, peer_reveal, peer_begin_ccar, peer_final_reflection],
                    api_visibility="private",
                )
                peer_a_submit.click(
                    _peer_a_submit,
                    [peer_state, peer_a_choice, peer_a_reflection],
                    [peer_state, peer_a_panel, peer_pass_panel, peer_pass_message],
                    api_visibility="private",
                )
                peer_show_b.click(
                    _show_peer_b,
                    peer_state,
                    [peer_prompt, peer_b_panel, peer_pass_panel],
                    api_visibility="private",
                )
                peer_b_submit.click(
                    _peer_b_submit,
                    [peer_state, peer_b_choice, peer_b_reflection],
                    [peer_state, peer_b_panel, peer_reveal, peer_begin_ccar, peer_final_reflection],
                    api_visibility="private",
                )
                peer_begin_ccar.click(
                    _begin_peer_ccar,
                    peer_state,
                    [peer_state, peer_prompt, peer_a_panel, peer_a_choice, peer_a_reflection, peer_begin_ccar],
                    api_visibility="private",
                )

            with gr.Tab("Model Results"):
                gr.Markdown(
                    "These results are revealed here for study after the decision exercise. They use the validated stylized model."
                )
                with gr.Accordion("What does the computational model predict?", open=True):
                    gr.Markdown(computational_results_markdown())
                with gr.Accordion("Verified priority-slot allocation results", open=False):
                    gr.Markdown(auction_results_markdown())
                gr.Markdown(f'<div class="evidence">{EVIDENCE_BOUNDARY}</div>')

            with gr.Tab("About / Methods"):
                gr.Markdown(
                    f"""
## Research question
{RESEARCH_QUESTION}

## Model
- **Players:** two competing commercial drone operators.
- **Actions:** Minimum, Partial, or Full voluntary disclosure. Mandatory safety data are always available.
- **Private information:** independent Low/High commercial-confidentiality sensitivity, each with prior probability 0.5.
- **Public information:** Low, Medium, or High congestion.
- **Benchmark:** pure-strategy Bayesian Nash equilibrium of a simultaneous static game.
- **Social welfare:** the sum of both operators' modeled utilities; no disclosure-model payments.
- **Full-information first best:** the welfare-maximizing action profile for a planner observing both realized types. It may not be implementable.
- **CCAR:** changes access only to enhanced non-safety coordination information; benchmark `alpha_M=0.7` at Medium/High congestion.
- **Auction:** a bounded downstream allocation exercise for one eligible non-emergency commercial slot.

## Data and privacy
No account, login, name, email, student ID, IP-address field, external API, or LLM API is used. Choices and free-text reflections remain in Gradio session state or unsaved browser inputs. No durable dataset or persistent counter is claimed.

## Limitations
Pure-strategy analysis; two operators; independent private types; three discrete disclosure levels; stylized parameters; potentially non-implementable first best; multiple-equilibrium parameter regions; omitted CCAR implementation/enforcement costs; and potentially interdependent real mission values.

<div class="evidence">{EVIDENCE_BOUNDARY}</div>
"""
                )
    return demo


demo = build_app()


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        theme=gr.themes.Soft(primary_hue="slate", secondary_hue="amber"),
        css=CSS,
        footer_links=["gradio", "settings"],
    )

