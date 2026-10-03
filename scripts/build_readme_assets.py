"""Build deterministic, GitHub-safe SVG assets for the public README.

Quantitative content is read from tracked validated CSV/JSON outputs. The SVGs
use explicit light backgrounds so labels remain readable in GitHub light and
dark modes. No network access, local absolute paths, or external images are
used.
"""

from __future__ import annotations

import csv
import html
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "assets" / "readme"
TABLE_DIR = ROOT / "outputs" / "tables"

INK = "#0F172A"
MUTED = "#475569"
BLUE = "#0B3D91"
ROYAL = "#2563EB"
TEAL = "#0F766E"
GREEN = "#15803D"
ORANGE = "#C2410C"
RED = "#B91C1C"
LINE = "#CBD5E1"
PALE = "#F8FAFC"
WHITE = "#FFFFFF"
BLUE_PALE = "#EAF2FF"
GREEN_PALE = "#EAF8F2"
ORANGE_PALE = "#FFF3E8"

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
ACTIONS = {"M": "Minimum", "P": "Partial", "F": "Full"}


def csv_rows(name: str) -> list[dict[str, str]]:
    with (TABLE_DIR / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(
    x: float,
    y: float,
    lines: str | list[str],
    *,
    size: int = 20,
    color: str = INK,
    weight: int = 400,
    anchor: str = "start",
    line_height: int | None = None,
    italic: bool = False,
) -> str:
    if isinstance(lines, str):
        lines = [lines]
    spacing = line_height or round(size * 1.25)
    tspans = []
    style = "italic" if italic else "normal"
    # Separate text elements are more consistent than multiline ``tspan`` blocks:
    # GitHub browsers and macOS's lightweight SVG previewer agree on the layout.
    for index, line in enumerate(lines):
        line_y = y + index * spacing
        tspans.append(
            f'<text x="{x}" y="{line_y}" text-anchor="{anchor}" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'font-style="{style}" fill="{color}">{esc(line)}</text>'
        )
    return "".join(tspans)


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str = WHITE,
    stroke: str = LINE,
    radius: int = 18,
    stroke_width: int = 2,
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def arrow(x1: float, y1: float, x2: float, y2: float, color: str = ROYAL) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="4" stroke-linecap="round" '
        f'marker-end="url(#arrow-{color[1:]})"/>'
    )


def compact_arrow(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = ROYAL,
    *,
    stroke_width: int = 3,
    head_length: int = 12,
    head_half_width: int = 7,
) -> str:
    """Draw a small self-contained arrow that stays inside narrow node gaps."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError("Arrow endpoints must be distinct")
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    base_x = x2 - ux * head_length
    base_y = y2 - uy * head_length
    left_x = base_x + px * head_half_width
    left_y = base_y + py * head_half_width
    right_x = base_x - px * head_half_width
    right_y = base_y - py * head_half_width
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{base_x}" y2="{base_y}" '
        f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
        f'<polygon points="{x2},{y2} {left_x},{left_y} {right_x},{right_y}" fill="{color}"/>'
    )


def svg_document(width: int, height: int, title_value: str, description: str, body: str) -> str:
    marker_colors = [ROYAL, TEAL, ORANGE]
    markers = "".join(
        f'<marker id="arrow-{color[1:]}" markerWidth="10" markerHeight="10" '
        f'refX="8" refY="3" orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L0,6 L9,3 z" fill="{color}"/></marker>'
        for color in marker_colors
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">\n'
        f'<title id="title">{esc(title_value)}</title>\n'
        f'<desc id="desc">{esc(description)}</desc>\n'
        f'<defs>{markers}</defs>\n'
        f'<rect width="{width}" height="{height}" rx="24" fill="{PALE}"/>\n'
        f'{body}\n</svg>\n'
    )


def write_svg(name: str, width: int, height: int, title_value: str, description: str, body: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / name).write_text(
        svg_document(width, height, title_value, description, body), encoding="utf-8"
    )


def load_data() -> dict[str, object]:
    bne_rows = csv_rows("baseline_bne_summary.csv")
    welfare_rows = csv_rows("baseline_welfare_gap.csv")
    ccar_rows = csv_rows("ccar_bne_summary.csv")
    auction_rows = csv_rows("auction_benchmark_example.csv")
    simulation_rows = csv_rows("auction_simulation_summary.csv")
    exported = json.loads((ROOT / "hf_static" / "data" / "validated_model_data.json").read_text())

    bne: dict[str, dict[str, object]] = {}
    for row in bne_rows:
        assert row["Operator A low-type action"] == row["Operator B low-type action"]
        assert row["Operator A high-type action"] == row["Operator B high-type action"]
        bne[row["Congestion"]] = {
            "d": float(row["d"]),
            "low": ACTIONS[row["Operator A low-type action"]],
            "high": ACTIONS[row["Operator A high-type action"]],
        }

    welfare = {
        row["Congestion"]: {
            "bne": float(row["BNE welfare"]),
            "first_best": float(row["Full-information first-best welfare"]),
            "gap": float(row["Welfare gap"]),
        }
        for row in welfare_rows
    }
    ccar_by_congestion = {row["Congestion"]: row for row in ccar_rows}
    medium_ccar = ccar_by_congestion["Medium"]
    ccar_strategy = medium_ccar["A strategy (L,H)"].strip("()").replace(" ", "").split(",")
    assert medium_ccar["A strategy (L,H)"] == medium_ccar["B strategy (L,H)"]

    auction_by_name = {row["mechanism"]: row for row in auction_rows}
    simulation_by_name = {row["mechanism"]: row for row in simulation_rows}
    benchmark = exported["auction"]["benchmark_example"]
    monte_carlo = exported["auction"]["monte_carlo"]

    return {
        "bne": bne,
        "welfare": welfare,
        "ccar": {
            "alpha": float(medium_ccar["alpha_M"]),
            "low": ACTIONS[ccar_strategy[0]],
            "high": ACTIONS[ccar_strategy[1]],
            "welfare": float(medium_ccar["Underlying expected welfare"]),
            "first_best": float(medium_ccar["Full-information first-best welfare"]),
        },
        "auction": {
            "benchmark": benchmark,
            "fcfs": auction_by_name["FCFS"],
            "second": auction_by_name["Second-price auction (truthful IPV benchmark)"],
            "fcfs_sim": simulation_by_name["FCFS"],
            "second_sim": simulation_by_name["Second-price auction (truthful IPV benchmark)"],
            "monte_carlo": monte_carlo,
        },
    }


def build_pipeline() -> None:
    stages = [
        ["Congestion d +", "private cost cᵢ"],
        ["Choose disclosure", "Minimum / Partial / Full"],
        ["Compute", "pure-strategy BNE"],
        ["Compare with", "full-information first best"],
        ["Measure", "welfare gap"],
        ["Test candidate", "CCAR"],
        ["Map", "robustness regions"],
        ["Allocate downstream", "priority slot"],
        ["Probe behavior", "Decision Lab"],
    ]
    body = text(60, 55, "From private information to testable institutional design", size=31, color=BLUE, weight=700)
    card_w, card_h, gap = 220, 100, 34
    top_y, bottom_y = 92, 252
    positions: list[tuple[float, float]] = []
    for index in range(5):
        positions.append((22 + index * (card_w + gap), top_y))
    for index in range(4):
        positions.append((149 + index * (card_w + gap), bottom_y))
    for index, ((x, y), lines) in enumerate(zip(positions, stages), 1):
        color = BLUE if index <= 5 else TEAL
        fill = BLUE_PALE if index <= 5 else GREEN_PALE
        body += rect(x, y, card_w, card_h, fill=fill, stroke=color, radius=14)
        body += f'<circle cx="{x + 24}" cy="{y + 25}" r="15" fill="{color}"/>'
        body += text(x + 24, y + 31, str(index), size=15, color=WHITE, weight=700, anchor="middle")
        body += text(x + card_w / 2, y + 45, lines, size=17, color=INK, weight=650, anchor="middle", line_height=22)
    for index in range(4):
        x, y = positions[index]
        nx, ny = positions[index + 1]
        body += compact_arrow(x + card_w + 6, y + card_h / 2, nx - 10, ny + card_h / 2)
    x5, y5 = positions[4]
    x6, y6 = positions[5]
    body += (
        f'<path d="M {x5 + card_w / 2} {y5 + card_h + 6} L {x5 + card_w / 2} 226 '
        f'L {x6 + card_w / 2} 226" fill="none" stroke="{TEAL}" stroke-width="3" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<polygon points="{x6 + card_w / 2},{y6 - 10} {x6 + card_w / 2 - 7},226 '
        f'{x6 + card_w / 2 + 7},226" fill="{TEAL}"/>'
    )
    for index in range(5, 8):
        x, y = positions[index]
        nx, ny = positions[index + 1]
        body += compact_arrow(x + card_w + 6, y + card_h / 2, nx - 10, ny + card_h / 2, TEAL)
    write_svg(
        "project_pipeline.svg",
        1280,
        390,
        "Project pipeline",
        "Nine-stage pipeline from congestion and private confidentiality cost through disclosure, equilibrium, welfare, CCAR, robustness, allocation, and the behavioral Decision Lab.",
        body,
    )


def build_bne_matrix(data: dict[str, object]) -> None:
    bne = data["bne"]
    assert isinstance(bne, dict)
    body = text(50, 54, "Type-contingent pure BNE under the benchmark", size=31, color=BLUE, weight=700)
    body += text(50, 86, "Rows = public congestion  ·  Columns = operator private confidentiality type", size=18, color=MUTED)
    x0, y0 = 235, 125
    col_w, row_h = 315, 88
    body += rect(x0, y0, col_w * 2, 58, fill=BLUE, stroke=BLUE, radius=10)
    body += text(x0 + col_w / 2, y0 + 37, "LOW TYPE", size=19, color=WHITE, weight=700, anchor="middle")
    body += text(x0 + col_w * 1.5, y0 + 37, "HIGH TYPE", size=19, color=WHITE, weight=700, anchor="middle")
    for row_index, congestion in enumerate(["Low", "Medium", "High"]):
        row = bne[congestion]
        assert isinstance(row, dict)
        y = y0 + 70 + row_index * row_h
        body += text(205, y + 34, congestion.upper(), size=20, color=BLUE, weight=700, anchor="end")
        body += text(205, y + 60, f'd = {float(row["d"]):.1f}', size=16, color=MUTED, anchor="end")
        for column_index, key in enumerate(["low", "high"]):
            action = str(row[key])
            fill = BLUE_PALE if action == "Minimum" else GREEN_PALE
            stroke = ROYAL if action == "Minimum" else TEAL
            x = x0 + column_index * col_w
            body += rect(x, y, col_w - 12, row_h - 12, fill=fill, stroke=stroke, radius=12)
            body += text(x + (col_w - 12) / 2, y + 46, action, size=24, color=INK, weight=700, anchor="middle")
    body += rect(165, 465, 670, 38, fill=WHITE, stroke=LINE, radius=10)
    body += text(500, 490, "Minimum = safety floor only   ·   Partial = added voluntary coordination detail", size=16, color=MUTED, anchor="middle")
    write_svg(
        "bne_matrix.svg",
        1000,
        530,
        "Benchmark Bayesian Nash equilibrium matrix",
        "A labeled three-by-two matrix showing Minimum for both types at low congestion, Partial and Minimum at medium congestion, and Partial for both types at high congestion.",
        body,
    )


def build_welfare_gap(data: dict[str, object]) -> None:
    welfare = data["welfare"]
    assert isinstance(welfare, dict)
    ordered = [(name, float(welfare[name]["gap"])) for name in ["Low", "Medium", "High"]]
    top = math.ceil(max(value for _, value in ordered) * 4) / 4
    body = text(50, 54, "Why medium congestion matters", size=31, color=BLUE, weight=700)
    body += text(50, 86, "Welfare gap = full-information first best − Bayesian equilibrium", size=18, color=MUTED)
    chart_left, chart_top, chart_bottom = 150, 125, 415
    chart_height = chart_bottom - chart_top
    for tick_index in range(5):
        tick = top * tick_index / 4
        y = chart_bottom - chart_height * tick / top
        body += f'<line x1="{chart_left}" y1="{y}" x2="920" y2="{y}" stroke="{LINE}" stroke-width="1"/>'
        body += text(chart_left - 16, y + 6, f"{tick:.2f}", size=15, color=MUTED, anchor="end")
    colors = [ROYAL, ORANGE, TEAL]
    fills = [BLUE_PALE, ORANGE_PALE, GREEN_PALE]
    xs = [260, 500, 740]
    for (name, value), x, color, fill in zip(ordered, xs, colors, fills):
        height = chart_height * value / top
        y = chart_bottom - height
        body += rect(x, y, 150, height, fill=fill, stroke=color, radius=10, stroke_width=3)
        body += text(x + 75, y - 14, f"{value:.3f}", size=24, color=color, weight=750, anchor="middle")
        body += text(x + 75, chart_bottom + 36, name.upper(), size=19, color=INK, weight=700, anchor="middle")
    body += text(500, 495, "At high congestion both types choose Partial; at medium congestion the high-cost type still chooses Minimum.", size=16, color=MUTED, anchor="middle")
    write_svg(
        "welfare_gap.svg",
        1000,
        525,
        "Welfare gap by congestion",
        "Three labeled bars show welfare gaps of approximately 0.639 at low, 0.946 at medium, and 0.503 at high congestion, highlighting the medium state.",
        body,
    )


def build_ccar(data: dict[str, object]) -> None:
    bne = data["bne"]
    welfare = data["welfare"]
    ccar = data["ccar"]
    assert isinstance(bne, dict) and isinstance(welfare, dict) and isinstance(ccar, dict)
    baseline = bne["Medium"]
    baseline_welfare = float(welfare["Medium"]["bne"])
    baseline_gap = float(welfare["Medium"]["gap"])
    ccar_welfare = float(ccar["welfare"])
    ccar_gap = float(ccar["first_best"]) - ccar_welfare
    body = text(50, 54, "CCAR at medium congestion", size=31, color=BLUE, weight=700)
    body += text(50, 86, "Congestion-Contingent Access Rule · candidate mechanism", size=18, color=MUTED)
    body += rect(50, 120, 380, 230, fill=BLUE_PALE, stroke=ROYAL, radius=18, stroke_width=3)
    body += text(240, 158, "BASELINE", size=20, color=ROYAL, weight=750, anchor="middle")
    body += text(90, 205, [f'Low type   {baseline["low"]}', f'High type  {baseline["high"]}'], size=22, color=INK, weight=650, line_height=42)
    body += text(90, 306, [f"Welfare  {baseline_welfare:.3f}", f"Gap          {baseline_gap:.3f}"], size=18, color=MUTED, line_height=28)
    body += rect(465, 145, 170, 66, fill=ORANGE_PALE, stroke=ORANGE, radius=12)
    body += text(550, 174, ["CCAR", f'alpha_M = {float(ccar["alpha"]):.1f}'], size=17, color=ORANGE, weight=750, anchor="middle", line_height=22)
    body += compact_arrow(450, 252, 650, 252, ORANGE)
    body += rect(670, 120, 380, 230, fill=GREEN_PALE, stroke=TEAL, radius=18, stroke_width=3)
    body += text(860, 158, "WITH CCAR", size=20, color=TEAL, weight=750, anchor="middle")
    body += text(710, 205, [f'Low type   {ccar["low"]}', f'High type  {ccar["high"]}'], size=22, color=INK, weight=650, line_height=42)
    body += text(710, 306, [f"Welfare  {ccar_welfare:.3f}", f"Gap          {ccar_gap:.3f}"], size=18, color=MUTED, line_height=28)
    body += rect(50, 378, 1000, 58, fill=WHITE, stroke=LINE, radius=14)
    body += text(550, 404, ["Mandatory safety information remains universal and unchanged.", "Mechanism performance is parameter-dependent."], size=17, color=INK, weight=650, anchor="middle", line_height=22)
    write_svg(
        "ccar_before_after.svg",
        1100,
        465,
        "CCAR before and after comparison",
        "At medium congestion, CCAR changes the high confidentiality type from Minimum to Partial, raises underlying welfare, and reduces the benchmark gap while leaving mandatory safety information universal.",
        body,
    )


def build_auction(data: dict[str, object]) -> None:
    auction = data["auction"]
    assert isinstance(auction, dict)
    benchmark = auction["benchmark"]
    fcfs = auction["fcfs"]
    second = auction["second"]
    monte_carlo = auction["monte_carlo"]
    values = benchmark["values"]
    order = benchmark["arrival_order"]
    values_text = "   ".join(f"{key}  {float(value):.0f}" for key, value in values.items())
    order_text = " → ".join(order)
    body = text(50, 54, "Week 5 downstream priority-slot allocation", size=31, color=BLUE, weight=700)
    body += text(50, 86, "One commercial slot · emergency/public-safety missions remain outside payment", size=18, color=MUTED)
    body += rect(50, 112, 1100, 62, fill=WHITE, stroke=LINE, radius=14)
    body += text(600, 151, f"Illustrative normalized values:  {values_text}", size=20, color=INK, weight=650, anchor="middle")
    body += rect(50, 198, 500, 225, fill=BLUE_PALE, stroke=ROYAL, radius=18, stroke_width=3)
    body += text(300, 238, "FIRST-COME, FIRST-SERVED", size=20, color=ROYAL, weight=750, anchor="middle")
    body += text(300, 274, f"Arrival: {order_text}", size=18, color=MUTED, anchor="middle")
    body += text(100, 325, [f'Winner  {fcfs["winner"]}', f'Allocated value  {float(fcfs["allocated_value"]):.0f}', f'Efficiency  {100 * float(fcfs["allocative_efficiency"]):.1f}%'], size=21, color=INK, weight=650, line_height=31)
    body += rect(650, 198, 500, 225, fill=GREEN_PALE, stroke=TEAL, radius=18, stroke_width=3)
    body += text(900, 238, "SECOND-PRICE BENCHMARK", size=20, color=TEAL, weight=750, anchor="middle")
    body += text(700, 291, [f'Winner  {second["winner"]}', f'Payment  {float(second["payment"]):.0f}   ·   Winner utility  {float(second["winner_utility"]):.0f}', f'Efficiency  {100 * float(second["allocative_efficiency"]):.0f}%'], size=21, color=INK, weight=650, line_height=38)
    body += rect(50, 450, 1100, 64, fill=WHITE, stroke=LINE, radius=14)
    body += text(600, 478, [f'{int(monte_carlo["rounds"]):,} rounds · {int(monte_carlo["eligible_bidders"])} bidders · {monte_carlo["distribution"]}', f'Mean efficiency: FCFS {float(monte_carlo["fcfs_mean_efficiency"]):.4f} · second price {float(monte_carlo["truthful_second_price_mean_efficiency"]):.4f}'], size=17, color=INK, weight=650, anchor="middle", line_height=22)
    body += text(600, 548, "Downstream scarcity-allocation application — not the core disclosure mechanism.", size=17, color=RED, weight=700, anchor="middle")
    write_svg(
        "auction_comparison.svg",
        1200,
        575,
        "FCFS and second-price auction comparison",
        "A labeled comparison of the illustrative FCFS and truthful second-price outcomes plus the validated ten-thousand-round simulation efficiency summary.",
        body,
    )


def build_three_lenses() -> None:
    cards = [
        (70, BLUE_PALE, ROYAL, "GAME THEORY", ["private types", "disclosure strategy", "Bayesian equilibrium"]),
        (430, ORANGE_PALE, ORANGE, "SOCIAL CHOICE", ["welfare", "first best", "efficiency + fairness"]),
        (790, GREEN_PALE, TEAL, "MECHANISM DESIGN", ["CCAR", "incentives", "allocation rule"]),
    ]
    body = text(50, 54, "Three disciplinary lenses", size=31, color=BLUE, weight=700)
    body += text(50, 86, "Each lens changes the question the project can answer", size=18, color=MUTED)
    for x, fill, stroke, heading, lines in cards:
        body += rect(x, 125, 330, 190, fill=fill, stroke=stroke, radius=18, stroke_width=3)
        body += text(x + 165, 167, heading, size=20, color=stroke, weight=750, anchor="middle")
        body += text(x + 165, 211, lines, size=20, color=INK, weight=600, anchor="middle", line_height=30)
        body += arrow(x + 165, 326, 600, 382, stroke)
    body += rect(260, 388, 680, 88, fill=WHITE, stroke=BLUE, radius=18, stroke_width=3)
    body += text(600, 422, "INTERDISCIPLINARY SYNTHESIS", size=21, color=BLUE, weight=750, anchor="middle")
    body += text(600, 454, "strategic behavior  +  collective value  +  institution design", size=20, color=INK, weight=650, anchor="middle")
    write_svg(
        "three_lenses.svg",
        1200,
        510,
        "Three disciplinary lenses",
        "Game theory, social choice, and mechanism design flow into an interdisciplinary synthesis of strategic behavior, collective value, and institution design.",
        body,
    )


def build_behavioral_lab() -> None:
    body = text(50, 54, "Behavioral Decision Lab", size=31, color=BLUE, weight=700)
    body += text(50, 86, "Interactive probes for reflection—not population evidence", size=18, color=MUTED)
    lanes = [
        (125, "SOLO", ["Decision", "Benchmark reveal", "CCAR decision", "Reflection"], ROYAL, BLUE_PALE, 190, 36),
        (245, "PEER PLAY", ["Private type", ["Pass-the-screen", "choice"], "Reveal"], TEAL, GREEN_PALE, 240, 48),
        (365, "AUCTION", ["Priority-slot", "choice exercise"], ORANGE, ORANGE_PALE, 260, 56),
    ]
    flow_left, flow_right = 245, 1135
    for y, label, steps, color, fill, card_w, gap in lanes:
        body += text(155, y + 42, label, size=18, color=color, weight=750, anchor="middle")
        n = len(steps)
        total_width = n * card_w + (n - 1) * gap
        start_x = flow_left + (flow_right - flow_left - total_width) / 2
        for index, step in enumerate(steps):
            x = start_x + index * (card_w + gap)
            body += rect(x, y, card_w, 78, fill=fill, stroke=color, radius=14, stroke_width=2)
            if isinstance(step, list):
                body += text(x + card_w / 2, y + 33, step, size=17, color=INK, weight=650, anchor="middle", line_height=22)
            else:
                body += text(x + card_w / 2, y + 46, step, size=18, color=INK, weight=650, anchor="middle")
            if index < n - 1:
                body += compact_arrow(x + card_w + 7, y + 39, x + card_w + gap - 11, y + 39, color)
    body += rect(90, 470, 1020, 62, fill=WHITE, stroke=RED, radius=14, stroke_width=2)
    body += text(600, 496, ["Evidence boundary: exploratory classroom decision artifact.", "Not representative evidence about real drone operators."], size=17, color=RED, weight=700, anchor="middle", line_height=21)
    write_svg(
        "behavioral_lab.svg",
        1200,
        560,
        "Behavioral Decision Lab flow",
        "Solo Decision, Peer Play, and auction exercise flows with an explicit exploratory evidence boundary.",
        body,
    )


def main() -> None:
    data = load_data()
    build_pipeline()
    build_bne_matrix(data)
    build_welfare_gap(data)
    build_ccar(data)
    build_auction(data)
    build_three_lenses()
    build_behavioral_lab()
    print(f"Wrote 7 README SVGs to {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
