#!/usr/bin/env python3
"""
personality_report_safe_vA.py
Complete, fault-tolerant PDF report generator.
Option A behaviour: missing charts/sections are SKIPPED entirely.
"""

import os
from datetime import datetime
import io
import json

import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.lib.units import cm

# ---------------------------
# Styling / constants
# ---------------------------
COLORS = {
    "primary": "#1E3A8A",
    "secondary": "#3B82F6",
    "accent": "#DBEAFE",
    "title": "#0F172A",
    "contrast": "#FC7C56",
    "sidebar": "#273C66",
    "body_text": "#334155",
    "subtle_text": "#64748B",
    "grid_lines": "#CBD5E1",
    "gauge_background": "#E2E8F0",
    "white": "#FFFFFF",
}

CHART_COLORS = [
    "#3B82F6",
    "#60A5FA",
    "#9333EA",
    "#F59E0B",
    "#10B981",
    "#EF4444",
    "#8B5CF6",
    "#F97316",
    "#0EA5E9",
    "#14B8A6",
]

username = "Utsav Lankapati"
REPORT_TITLE = f"{username} Profile Report"
COMPANY_NAME = "Endorphin"
company_info_mail = "info.endorphin@gamil.com"
company_site = "www.endorphin.in"

PAGE_WIDTH, PAGE_HEIGHT = A4


# ---------------------------
# Safe helpers
# ---------------------------
def safe_get(obj, path, default=None):
    """Safely retrieve nested keys like safe_get(data, 'sections.charts.radarChart.data')"""
    if obj is None:
        return default
    if isinstance(path, str) and path == "":
        return obj
    keys = path.split(".")
    cur = obj
    for key in keys:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def is_nonempty_list(x):
    return isinstance(x, list) and len(x) > 0


def is_valid_number(x):
    try:
        if x is None:
            return False
        float(x)
        return True
    except Exception:
        return False


# ---------------------------
# Placeholder logo generator
# ---------------------------
def make_placeholder_logo(
    size=(240, 240), bg=COLORS["primary"], circle=COLORS["accent"]
):
    img = Image.new("RGBA", size, bg)
    draw = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    r_outer = min(size) // 2 - 10
    points = []
    for i in range(6):
        angle = np.pi / 2 + (2 * np.pi * i / 6)
        x = cx + r_outer * np.cos(angle)
        y = cy - r_outer * np.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=bg, outline=COLORS["secondary"])
    r_inner = int(r_outer * 0.6)
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=circle)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=bg)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# ---------------------------
# Chart creators (called only when data present)
# ---------------------------
def create_radar_chart(radar_entries):
    if not is_nonempty_list(radar_entries):
        raise ValueError("Radar entries must be a non-empty list")
    labels = [
        str(e.get("field", "")) for e in radar_entries if "field" in e and "value" in e
    ]
    values = [float(e["value"]) for e in radar_entries if "field" in e and "value" in e]
    if len(labels) == 0:
        raise ValueError("Radar entries contain no valid items")
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    plt.style.use("default")
    fig = plt.figure(figsize=(6, 6), dpi=200, facecolor="none")
    ax = fig.add_subplot(111, polar=True, facecolor="none")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(
        angles_closed,
        values_closed,
        linewidth=2.5,
        linestyle="solid",
        color=COLORS["primary"],
    )
    ax.fill(
        angles_closed,
        values_closed,
        alpha=0.55,
        facecolor=COLORS["secondary"],
        edgecolor=COLORS["primary"],
        linewidth=1,
    )

    ax.set_thetagrids(np.degrees(angles), labels, fontsize=9, color=COLORS["title"])
    ax.tick_params(axis="y", colors=COLORS["subtle_text"])
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_rlabel_position(180 / max(1, N))
    ax.grid(color=COLORS["grid_lines"], linestyle="-", linewidth=0.7)
    ax.spines["polar"].set_visible(False)

    fig.patch.set_alpha(0.0)
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def create_horizontal_bar_chart(bar_entries, title="Score Summary"):
    if not is_nonempty_list(bar_entries):
        raise ValueError("Bar entries must be a non-empty list")
    labels = [
        str(e.get("field", "")) for e in bar_entries if "field" in e and "value" in e
    ]
    values = [float(e["value"]) for e in bar_entries if "field" in e and "value" in e]
    if len(labels) == 0:
        raise ValueError("Bar entries contain no valid items")

    N = len(labels)
    bar_colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(N)]
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(7, 3.5), dpi=200, facecolor="none")
    y_pos = np.arange(N)
    bars = ax.barh(y_pos, values, align="center", color=bar_colors, linewidth=0)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9, color=COLORS["title"])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Profile Score (0-100)", color=COLORS["primary"], fontsize=10)
    ax.tick_params(axis="x", colors=COLORS["subtle_text"])
    ax.grid(axis="x", linestyle="--", linewidth=0.5, color="#DDDDDD")
    ax.set_title(title, fontsize=12, color=COLORS["primary"], fontweight="bold", pad=10)
    for i, b in enumerate(bars):
        ax.text(
            b.get_width() + 1,
            b.get_y() + b.get_height() / 2,
            f"{int(values[i])}",
            va="center",
            fontsize=9,
            color=COLORS["primary"],
            fontweight="bold",
        )
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.spines["bottom"].set_linewidth(0.5)
    fig.patch.set_alpha(0.0)
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def create_vertical_bar_chart(bar_entries, title="Score Summary"):
    if not is_nonempty_list(bar_entries):
        raise ValueError("Vertical bar entries must be a non-empty list")
    labels = [
        str(e.get("field", "")) for e in bar_entries if "field" in e and "value" in e
    ]
    values = [float(e["value"]) for e in bar_entries if "field" in e and "value" in e]
    if len(labels) == 0:
        raise ValueError("Vertical bar entries contain no valid items")
    N = len(labels)
    bar_colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(N)]
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(7, 3.5), dpi=200, facecolor="none")
    x_pos = np.arange(N)
    bars = ax.bar(x_pos, values, align="center", color=bar_colors, linewidth=0)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=9, color=COLORS["title"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Profile Score (0-100)", color=COLORS["primary"], fontsize=10)
    ax.tick_params(axis="y", colors=COLORS["subtle_text"])
    ax.grid(axis="y", linestyle="--", linewidth=0.5, color="#DDDDDD")
    ax.set_title(title, fontsize=12, color=COLORS["primary"], fontweight="bold", pad=10)
    for i, b in enumerate(bars):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + 1,
            f"{int(values[i])}",
            ha="center",
            fontsize=9,
            color=COLORS["primary"],
            fontweight="bold",
        )
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.spines["bottom"].set_linewidth(0.5)
    fig.patch.set_alpha(0.0)
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def create_comparison_bar_chart(entries, title="Trait Comparison"):
    if not is_nonempty_list(entries):
        raise ValueError("Comparison entries must be a non-empty list")
    labels = [str(e.get("field", "")) for e in entries if "field" in e and "value" in e]
    user_values = [float(e["value"]) for e in entries if "field" in e and "value" in e]
    if len(labels) == 0:
        raise ValueError("Comparison entries contain no valid items")
    benchmark_values = [50] * len(labels)
    N = len(labels)

    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(8, 4), dpi=200, facecolor="none")
    x_pos = np.arange(N)
    ax.bar(
        x_pos - 0.2,
        user_values,
        width=0.4,
        align="center",
        color=CHART_COLORS[0],
        label="Your Score",
    )
    ax.bar(
        x_pos + 0.2,
        benchmark_values,
        width=0.4,
        align="center",
        color=CHART_COLORS[1],
        label="Benchmark",
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=9, color=COLORS["title"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Profile Score (0-100)", color=COLORS["primary"], fontsize=10)
    ax.tick_params(axis="y", colors=COLORS["subtle_text"])
    ax.grid(axis="y", linestyle="--", linewidth=0.5, color="#DDDDDD")
    ax.set_title(title, fontsize=12, color=COLORS["primary"], fontweight="bold", pad=10)
    ax.legend()
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.spines["bottom"].set_linewidth(0.5)
    fig.patch.set_alpha(0.0)
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def create_donut_chart(entries, title="Strengths Distribution"):
    if not is_nonempty_list(entries):
        raise ValueError("Donut entries must be a non-empty list")
    labels = [str(e.get("field", "")) for e in entries if "field" in e and "value" in e]
    values = [float(e["value"]) for e in entries if "field" in e and "value" in e]
    if len(labels) == 0:
        raise ValueError("Donut entries contain no valid items")
    chart_colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(labels))]
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(6, 6), dpi=200, facecolor="none")
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=chart_colors,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.85,
    )
    for autotext in autotexts:
        autotext.set_color(COLORS["white"])
        autotext.set_fontweight("bold")
    centre_circle = plt.Circle((0, 0), 0.70, fc=COLORS["white"])
    fig.gca().add_artist(centre_circle)
    ax.axis("equal")
    ax.set_title(title, fontsize=12, color=COLORS["primary"], fontweight="bold", pad=10)
    fig.patch.set_alpha(0.0)
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def create_gauge_chart(score, title="Risk Profile"):
    if not is_valid_number(score):
        raise ValueError("Gauge score must be numeric")
    score = float(score)
    score = max(0.0, min(100.0, score))
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=200, facecolor="none")
    ax.add_patch(
        patches.Circle(
            (0.5, 0.4), 0.4, color=COLORS["gauge_background"], fill=True, zorder=1
        )
    )
    ax.add_patch(
        patches.Circle((0.5, 0.4), 0.3, color=COLORS["white"], fill=True, zorder=1)
    )
    theta = 180 - score * 1.8
    ax.add_patch(
        patches.Wedge((0.5, 0.4), 0.4, 180, theta, color=COLORS["primary"], zorder=2)
    )
    ax.add_patch(
        patches.Circle((0.5, 0.4), 0.3, color=COLORS["white"], fill=True, zorder=3)
    )
    ax.text(
        0.5,
        0.4,
        f"{int(score)}",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=40,
        fontweight="bold",
        color=COLORS["primary"],
        zorder=4,
    )
    ax.text(
        0.5,
        0.25,
        title,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=12,
        color=COLORS["primary"],
        zorder=4,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_alpha(0.0)
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer


# ---------------------------
# PDF utilities: header/footer and small table helpers
# ---------------------------
def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor(COLORS["sidebar"]))
    canvas.rect(0, 0, 1.5 * cm, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.translate(1.0 * cm, 8 * cm)
    canvas.rotate(90)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(colors.HexColor(COLORS["white"]))
    canvas.drawString(0, 0, COMPANY_NAME)
    canvas.restoreState()

    canvas.saveState()
    canvas.setFillColor(colors.HexColor(COLORS["primary"]))
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(2.5 * cm, PAGE_HEIGHT - 2 * cm, REPORT_TITLE)
    canvas.setStrokeColor(colors.HexColor(COLORS["contrast"]))
    canvas.setLineWidth(1.5)
    canvas.line(
        2.5 * cm, PAGE_HEIGHT - 2.2 * cm, PAGE_WIDTH - 2 * cm, PAGE_HEIGHT - 2.2 * cm
    )

    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor(COLORS["primary"]))
    page_num_text = f"Page {canvas.getPageNumber()}"
    canvas.drawRightString(PAGE_WIDTH - 2 * cm, 1.4 * cm, page_num_text)

    canvas.setStrokeColor(colors.HexColor(COLORS["contrast"]))
    canvas.setLineWidth(1.5)
    canvas.line(2.5 * cm, 1.8 * cm, PAGE_WIDTH - 2 * cm, 1.8 * cm)

    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(colors.HexColor(COLORS["subtle_text"]))
    canvas.drawString(
        2.5 * cm,
        1.4 * cm,
        f"We are {COMPANY_NAME}, dedicated to advancing careers and well-being. | {company_site}",
    )
    canvas.restoreState()


def _create_chart_guide_table(data):
    styles = getSampleStyleSheet()
    if "BodyText" not in styles:
        styles.add(
            ParagraphStyle(
                name="BodyText", fontName="Helvetica", fontSize=10, leading=12
            )
        )
    wrapped_data = [
        [Paragraph(str(cell), styles["BodyText"]) for cell in row] for row in data
    ]
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COLORS["accent"])),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(COLORS["primary"])),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS["primary"])),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor(COLORS["accent"])]),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]
    )
    table = Table(wrapped_data, colWidths=[100, 350], hAlign="LEFT")
    table.setStyle(style)
    return table


def _create_data_table(data):
    styles = getSampleStyleSheet()
    if "BodyText" not in styles:
        styles.add(
            ParagraphStyle(
                name="BodyText", fontName="Helvetica", fontSize=10, leading=12
            )
        )
    wrapped_data = [
        [Paragraph(str(cell), styles["BodyText"]) for cell in row] for row in data
    ]
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COLORS["accent"])),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(COLORS["primary"])),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS["primary"])),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor(COLORS["accent"])]),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]
    )
    table = Table(wrapped_data, colWidths=[100, 350], hAlign="LEFT")
    table.setStyle(style)
    return table


def build_chart_story(title, chart_data, buffer, w, h, guide_data, styles):
    """Builds a story section for a single chart. chart_data is the original chart dict from JSON."""
    story = [
        Paragraph(title, styles["SectionHeader"]),
        Paragraph(
            (
                str(chart_data.get("explanation", ""))
                if isinstance(chart_data, dict)
                else ""
            ),
            styles["Body"],
        ),
        Spacer(1, 0.5 * cm),
        RLImage(buffer, width=w * cm, height=h * cm, hAlign="CENTER"),
        Spacer(1, 0.5 * cm),
        Paragraph("Chart Data", styles["TraitTitle"]),
    ]

    # Handle single-value charts like Gauge
    if (
        isinstance(chart_data, dict)
        and "data" in chart_data
        and is_nonempty_list(chart_data["data"])
    ):
        data_list = [
            [e.get("field", ""), e.get("value", "")]
            for e in chart_data["data"]
            if "field" in e and "value" in e
        ]
    else:
        # For charts like gauge -> value; for others if no 'data' available, try to present the title/value
        if isinstance(chart_data, dict) and "value" in chart_data:
            data_list = [[title.split(":")[0].strip(), chart_data.get("value", "N/A")]]
        else:
            data_list = [[title.split(":")[0].strip(), "N/A"]]

    story.append(_create_data_table([["Field", "Value"]] + data_list))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("How to Read This Chart", styles["TraitTitle"]))
    story.append(_create_chart_guide_table([["Element", "Description"]] + guide_data))
    return KeepTogether(story)


def add_static_pages(story, styles):
    """Adds the static introduction and explanation pages to the story."""
    story.append(Paragraph("1. Report Overview", styles["SectionHeader"]))
    story.append(
        Paragraph(
            "This <b>confidential report</b> summarizes your core personality, cognitive style, and motivational drivers. "
            "It is structured to provide an easy-to-digest profile for both personal growth and professional development.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Key Components:", styles["TraitTitle"]))
    for p in ["Trait Breakdown", "Graphical Summaries", "Recommendations"]:
        story.append(Paragraph(f"• {p}", styles["CustomBullet"]))
    story.append(PageBreak())

    story.append(Paragraph("2. How to Read This Report", styles["SectionHeader"]))
    story.append(
        Paragraph(
            "Each score reflects the intensity of the corresponding trait, interpreted along a standardized 1–10 scale.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Score Interpretation (1–10 Scale)", styles["TraitTitle"]))
    score_table_data = [
        [
            Paragraph(f"<b>{h}</b>", styles["Body"])
            for h in ["Score Range", "Interpretation", "Meaning"]
        ],
        [
            Paragraph("1–3", styles["Body"]),
            Paragraph("Low", styles["Body"]),
            Paragraph("Trait is less dominant.", styles["Body"]),
        ],
        [
            Paragraph("4–6", styles["Body"]),
            Paragraph("Balanced", styles["Body"]),
            Paragraph("Represents flexibility.", styles["Body"]),
        ],
        [
            Paragraph("7–10", styles["Body"]),
            Paragraph("High", styles["Body"]),
            Paragraph("Trait strongly defines behavior.", styles["Body"]),
        ],
    ]
    score_table = Table(score_table_data, colWidths=[70, 100, 300], repeatRows=1)
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COLORS["accent"])),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(COLORS["primary"])),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor(COLORS["accent"]), colors.white],
                ),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor(COLORS["primary"])),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(COLORS["secondary"])),
            ]
        )
    )
    story.append(score_table)
    story.append(PageBreak())


# ---------------------------
# Main generator (fault-tolerant)
# ---------------------------
def generate_personality_pdf(filename, data, person_name, generated_by):
    # Prepare logo (use file if present, else placeholder buffer)
    logo_path = "./endorphin.jpeg"
    if os.path.exists(logo_path):
        logo_buffer = logo_path
    else:
        logo_buffer = make_placeholder_logo()

    # Process and generate all charts in a data-driven way.
    # This configuration list drives chart creation. To add/remove a chart,
    # simply add/remove an entry from this list.
    chart_configs = [
        {
            "name": "Radar Chart",
            "page_title": "5. Radar Chart of Traits",
            "data_path": "sections.charts.radarChart",
            "value_key": "data",
            "validation_func": is_nonempty_list,
            "creation_func": create_radar_chart,
            "args": {},
            "w": 12,
            "h": 12,
            "guide_data": [
                ["Axes", "Each axis represents a different personality trait."],
                [
                    "Value",
                    "The further the point is from the center, the higher the score.",
                ],
            ],
        },
        {
            "name": "Bar Chart",
            "page_title": "6. Bar Chart Summary (Core Attributes)",
            "data_path": "sections.charts.barChart",
            "value_key": "data",
            "validation_func": is_nonempty_list,
            "creation_func": create_horizontal_bar_chart,
            "args": {"title": "Core Attribute Summary"},
            "w": 14,
            "h": 7,
            "guide_data": [
                ["Bars", "Each horizontal bar represents a core attribute."],
                ["Length", "The length of the bar corresponds to your score (0-100)."],
            ],
        },
        {
            "name": "Cognitive Chart",
            "page_title": "7. Cognitive Score Chart",
            "data_path": "sections.barChart",  # Note: Different path from other charts
            "value_key": "data",
            "validation_func": is_nonempty_list,
            "creation_func": create_vertical_bar_chart,
            "args": {"title": "Cognitive Score Summary"},
            "w": 14,
            "h": 7,
            "guide_data": [
                ["Bars", "Each vertical bar represents a cognitive ability."],
                ["Height", "The height of the bar shows your score."],
            ],
        },
        {
            "name": "Comparison Chart",
            "page_title": "8. Trait Comparison Chart",
            "data_path": "sections.charts.comparisonTable",
            "value_key": "data",
            "validation_func": is_nonempty_list,
            "creation_func": create_comparison_bar_chart,
            "args": {},
            "w": 16,
            "h": 8,
            "guide_data": [
                ["Your Score", "The dark bar representing your score."],
                [
                    "Benchmark",
                    "The lighter bar representing the population average (50).",
                ],
            ],
        },
        {
            "name": "Donut Chart",
            "page_title": "9. Donut Chart of Strengths",
            "data_path": "sections.charts.donutChart",
            "value_key": "data",
            "validation_func": is_nonempty_list,
            "creation_func": create_donut_chart,
            "args": {},
            "w": 12,
            "h": 12,
            "guide_data": [
                ["Slices", "Each slice represents a different strength."],
                ["Size", "The size of the slice corresponds to the score."],
            ],
        },
        {
            "name": "Gauge Chart",
            "page_title": "10. Gauge Chart: Risk Profile",
            "data_path": "sections.charts.gaugeChart",
            "value_key": "value",
            "validation_func": is_valid_number,
            "creation_func": create_gauge_chart,
            "args": {"title": "Risk Profile"},
            "w": 12,
            "h": 7,
            "guide_data": [
                ["Value", "The value represents the risk profile score."],
                ["Color", "The color of the gauge indicates the level of risk."],
            ],
        },
    ]

    chart_definitions = []
    for config in chart_configs:
        chart_meta = safe_get(data, config["data_path"], default=None)
        chart_value = safe_get(chart_meta, config["value_key"], default=None)

        if chart_meta and config["validation_func"](chart_value):
            try:
                buffer = config["creation_func"](chart_value, **config.get("args", {}))
                if buffer:
                    chart_definitions.append(
                        (
                            config["page_title"],
                            chart_meta,
                            buffer,
                            config["w"],
                            config["h"],
                            config["guide_data"],
                        )
                    )
            except Exception as e:
                # Add logging to see which chart is failing and why.
                print(f"[WARNING] Skipping chart '{config['name']}' due to error: {e}")
                continue

    # Build PDF doc
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2 * cm,
        topMargin=2.6 * cm,
        bottomMargin=2.2 * cm,
        title=f"{person_name} - {REPORT_TITLE}",
    )

    # Styles
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            alignment=1,
            fontSize=30,
            textColor=colors.HexColor(COLORS["title"]),
            spaceAfter=20,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            alignment=1,
            fontSize=14,
            textColor=colors.HexColor(COLORS["primary"]),
            spaceAfter=30,
            fontName="Helvetica",
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeader",
            fontSize=16,
            textColor=colors.HexColor(COLORS["primary"]),
            spaceAfter=10,
            spaceBefore=20,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="TraitTitle",
            fontSize=12,
            textColor=colors.HexColor(COLORS["title"]),
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="CenteredBody",
            fontSize=10,
            leading=16,
            textColor=colors.HexColor(COLORS["body_text"]),
            fontName="Helvetica",
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            fontSize=10,
            leading=16,
            textColor=colors.HexColor(COLORS["body_text"]),
            fontName="Helvetica",
        )
    )
    styles.add(
        ParagraphStyle(
            name="CustomBullet",
            parent=styles["Body"],
            leftIndent=0.5 * cm,
            firstLineIndent=-0.5 * cm,
        )
    )

    story = []

    # COVER
    story.append(Spacer(1, 6 * cm))
    # RLImage accepts either filename or file-like object.
    story.append(RLImage(logo_buffer, width=4.5 * cm, height=4.5 * cm, hAlign="CENTER"))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(f"<b>{person_name}'s</b>", styles["ReportTitle"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "Comprehensive Personality & Cognitive Profile", styles["ReportSubtitle"]
        )
    )
    story.append(Spacer(1, 1 * cm))
    story.append(
        Paragraph(
            f"Generated on: <b>{datetime.now().strftime('%B %d, %Y')}</b>",
            styles["CenteredBody"],
        )
    )
    story.append(Paragraph(f"{COMPANY_NAME} Inc.", styles["CenteredBody"]))
    story.append(
        Paragraph(f"{company_info_mail} | {company_site}", styles["CenteredBody"])
    )
    story.append(Spacer(1, 2 * cm))
    story.append(
        Paragraph(
            f"The Individual Profile of {person_name}'s Report Generated by {generated_by}.",
            styles["CenteredBody"],
        )
    )
    story.append(
        Paragraph("(Confidential — For recipient only.)", styles["CenteredBody"])
    )
    story.append(PageBreak())

    # TABLE OF CONTENTS (static, minimal)
    story.append(Paragraph("Table of Contents", styles["ReportTitle"]))
    story.append(Spacer(1, 0.5 * cm))
    toc_data = [
        ("Report Overview", 3),
        ("How to Read This Report", 4),
        ("Personality Breakdown", 5),
        ("Cognitive Profile", 6),
        ("Radar Chart", 7),
        ("Bar Chart", 8),
        ("Comparison Chart", 9),
        ("Donut Chart", 10),
        ("Gauge Chart", 11),
        ("Recommendations", 12),
        ("Next Steps", 13),
    ]
    toc_table_data = [
        [f"{i+1}.", title, f".... {page}"] for i, (title, page) in enumerate(toc_data)
    ]
    toc_table = Table(toc_table_data, colWidths=[30, 420, 50])
    toc_table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor(COLORS["title"])),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.HexColor(COLORS["secondary"]),
                ),
            ]
        )
    )
    story.append(toc_table)
    story.append(PageBreak())

    # STATIC PAGES
    add_static_pages(story, styles)

    # Personality Breakdown (safe)
    story.append(Paragraph("3. Personality Breakdown", styles["SectionHeader"]))
    report_section = safe_get(data, "sections.report", default={})
    if isinstance(report_section, dict) and len(report_section) > 0:
        for trait, desc in report_section.items():
            story.append(
                KeepTogether(
                    [
                        Paragraph(str(trait), styles["TraitTitle"]),
                        Paragraph(str(desc), styles["Body"]),
                        Spacer(1, 0.3 * cm),
                    ]
                )
            )
    else:
        # If section missing, we simply skip content (Option A)
        story.append(
            Paragraph("No personality breakdown data available.", styles["Body"])
        )
    story.append(PageBreak())

    # Cognitive intro
    story.append(Paragraph("4. Cognitive Profile Overview", styles["SectionHeader"]))
    story.append(
        Paragraph(
            "This section details your cognitive functioning. The following chart visualizes your performance across core cognitive domains.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(PageBreak())

    # The `chart_definitions` list is now built dynamically in the loop above.
    # This section is intentionally left blank.

    # Add chart pages — Option A: skip any chart missing metadata or buffer
    for title, chart_data, buffer, w, h, guide_data in chart_definitions:
        try:
            # If any critical piece missing, skip
            if not chart_data or buffer is None:
                continue
            story.append(
                build_chart_story(title, chart_data, buffer, w, h, guide_data, styles)
            )
            story.append(PageBreak())
        except Exception:
            # Skip problematic charts silently (Option A)
            continue

    # Recommendations & Next Steps (always include)
    story.append(Paragraph("11. Career Fit Recommendations", styles["SectionHeader"]))
    story.append(
        Paragraph(
            "These recommendations suggest environments and roles where you are likely to thrive.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 0.3 * cm))

    insights = [
        "<b>Strengths Leverage:</b> Utilize high openness and strong logical reasoning in roles requiring creativity and analytical problem-solving.",
        "<b>Growth Areas Focus:</b> Target spontaneous engagement and social energy development through varied networking opportunities.",
        "<b>Optimal Career Fit:</b> Analytical and structured roles (e.g., data analysis, engineering) are best suited.",
        "<b>Ideal Environment:</b> Seek environments that provide clear goals and autonomy.",
    ]
    for p in insights:
        story.append(Paragraph("• " + p, styles["CustomBullet"]))
    story.append(PageBreak())

    story.append(Paragraph("12. Next Steps", styles["SectionHeader"]))
    story.append(
        Paragraph(
            "Use these steps to integrate your profile results into your development goals.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    next_steps_list = [
        "<b>Discuss & Validate</b>: Share this report with a trusted mentor or coach.",
        "<b>Set a SMART Goal</b>: Choose one 'Growth Area' and set a specific, measurable goal for the next 90 days.",
        "<b>Track Success</b>: Document instances where your strengths helped you succeed.",
        "<b>Revisit in Six Months</b>: Personal development is cyclical. Revisit this report to measure growth.",
    ]
    for p in next_steps_list:
        story.append(Paragraph("• " + p, styles["CustomBullet"]))

    # Build PDF with header/footer
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


# ---------------------------
# CLI / run
# ---------------------------
if __name__ == "__main__":
    input_path = "question_report_data.json"
    if not os.path.exists(input_path):
        print(f"[ERROR] Input JSON file not found at {input_path}. Create it or change the path.")
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        outname = f"{username}_Personality_Report_SafeOptionA.pdf"
        try:
            generate_personality_pdf(outname, data, person_name=username, generated_by=username)
            print(f"[OK] Generated: {outname}")
        except Exception as e:
            print("[ERROR] Failed to generate PDF:", str(e))
