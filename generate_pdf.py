import os
from datetime import datetime
import io # Import for in-memory operations

import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.units import cm, inch

# --- FANCY STYLING CONSTANTS ---
PRIMARY_COLOR = "#00473E" # Deep Teal (Primary Text/Headers)
SECONDARY_COLOR = "#78A083" # Dusty Green (Chart Fills/Backgrounds)
ACCENT_COLOR = "#E6EED6" # Light Beige (Background/Striping)
TITLE_COLOR = "#121C14" # Very dark (High contrast text)
CONTRAST_COLOR = "#C65300" # Burnt Orange (Accent lines/highlights)
REPORT_TITLE = "PsyMitrix Individual Profile Report"

# ---------------------------
# Utility: create placeholder logo (Returns buffer)
# ---------------------------
def make_placeholder_logo(size=(240, 240), bg=PRIMARY_COLOR, circle=ACCENT_COLOR):
    img = Image.new("RGBA", size, bg)
    draw = ImageDraw.Draw(img)
    
    cx, cy = size[0]//2, size[1]//2
    r_outer = min(size)//2 - 10
    r_inner = int(r_outer * 0.6)
    
    # Draw a hexagon for a more modern, structured look
    points = []
    for i in range(6):
        angle = np.pi/2 + (2 * np.pi * i / 6)
        x = cx + r_outer * np.cos(angle)
        y = cy - r_outer * np.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=bg, outline=SECONDARY_COLOR, width=5)
    
    # Draw an inner circle
    draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], fill=circle)
    # small inner dot
    draw.ellipse([cx-12, cy-12, cx+12, cy+12], fill=bg)
    
    # Save to in-memory buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# ---------------------------
# Charts: radar and bar using matplotlib (Returns buffer)
# ---------------------------
def create_radar_chart(radar_entries):
    labels = [e['field'] for e in radar_entries]
    values = [e['value'] for e in radar_entries]
    values = [v * 10 for v in values]
    N = len(labels)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    plt.style.use('default') 
    fig = plt.figure(figsize=(6, 6), dpi=200, facecolor='none') 
    ax = fig.add_subplot(111, polar=True, facecolor='none') 
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles, values, linewidth=2.5, linestyle='solid', color=PRIMARY_COLOR)
    ax.fill(angles, values, alpha=0.55, facecolor=SECONDARY_COLOR, edgecolor=PRIMARY_COLOR, linewidth=1)

    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=9, color=TITLE_COLOR)
    ax.tick_params(axis='y', colors='#666666') 
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_rlabel_position(180 / N)
    ax.grid(color="#CCCCCC", linestyle='-', linewidth=0.7)
    ax.spines['polar'].set_visible(False)
    
    fig.patch.set_alpha(0.0) 
    
    plt.tight_layout()
    
    # Save to in-memory buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer

# Modified to accept a title for clarity since it's used for two different sections
def create_bar_chart(bar_entries, title="Score Summary"):
    labels = [e['field'] for e in bar_entries]
    values = [e['value'] for e in bar_entries]
    values = [v * 10 for v in values] # scale 1-10 to 0-100
    N = len(labels)
    
    # Use a sequential colormap for multi-color bars (Teal/Green palette)
    cmap = plt.cm.get_cmap('viridis', N)
    colors = cmap(np.linspace(0.1, 0.9, N))

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(7, 3.5), dpi=200, facecolor='none')
    y_pos = np.arange(N)
    
    bars = ax.barh(y_pos, values, align='center', color=colors, linewidth=0)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9, color=TITLE_COLOR)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Profile Score (0-100)", color=PRIMARY_COLOR, fontsize=10)
    ax.tick_params(axis='x', colors='#666666')
    ax.grid(axis='x', linestyle='--', linewidth=0.5, color='#DDDDDD')
    
    ax.set_title(title, fontsize=12, color=PRIMARY_COLOR, fontweight='bold', pad=10)
    
    for i, b in enumerate(bars):
        # Annotate score text
        ax.text(b.get_width() + 1, b.get_y() + b.get_height()/2, 
                f"{int(values[i])}", va='center', fontsize=9, color=PRIMARY_COLOR, fontweight='bold')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)

    fig.patch.set_alpha(0.0)

    plt.tight_layout()
    
    # Save to in-memory buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer

def create_comparison_bar_chart(entries, title="Trait Comparison"):
    labels = [e['field'] for e in entries]
    user_values = [e['value'] for e in entries]
    benchmark_values = [5 for _ in entries] # Benchmark is 5
    N = len(labels)

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(8, 4), dpi=200, facecolor='none')
    y_pos = np.arange(N)
    height = 0.35

    rects1 = ax.barh(y_pos - height/2, user_values, height, label='Your Score', color=PRIMARY_COLOR)
    rects2 = ax.barh(y_pos + height/2, benchmark_values, height, label='Benchmark', color=SECONDARY_COLOR)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10, color=TITLE_COLOR)
    ax.invert_yaxis()
    ax.set_xlim(0, 10)
    ax.set_xlabel("Score (1-10)", color=PRIMARY_COLOR, fontsize=10)
    ax.tick_params(axis='x', colors='#666666')
    ax.grid(axis='x', linestyle='--', linewidth=0.5, color='#DDDDDD')

    ax.set_title(title, fontsize=14, color=PRIMARY_COLOR, fontweight='bold', pad=15)
    ax.legend()

    # Add value labels
    for rect in rects1:
        width = rect.get_width()
        ax.text(width + 0.1, rect.get_y() + rect.get_height() / 2.0, f'{width}', ha='left', va='center', fontsize=8, color=PRIMARY_COLOR)

    for rect in rects2:
        width = rect.get_width()
        ax.text(width + 0.1, rect.get_y() + rect.get_height() / 2.0, f'{width}', ha='left', va='center', fontsize=8, color=SECONDARY_COLOR)

    fig.patch.set_alpha(0.0)
    plt.tight_layout()
    
    # Save to in-memory buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer

# ---------------------------
# PDF: header/footer
# ---------------------------
PAGE_WIDTH, PAGE_HEIGHT = A4
COMPANY_NAME = "PsyMitrix"
SIDE_BAR_COLOR = "#003A33" # Darker version of primary

def header_footer(canvas, doc):
    canvas.saveState()
    
    # Dark Vertical Sidebar
    canvas.setFillColor(colors.HexColor(SIDE_BAR_COLOR))
    canvas.rect(0, 0, 1.5*cm, PAGE_HEIGHT, fill=1, stroke=0)

    # Vertical Company Name
    canvas.translate(1.0*cm, 8*cm)
    canvas.rotate(90)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(colors.white) # White text for contrast
    canvas.drawString(0, 0, COMPANY_NAME)
    canvas.restoreState()
    
    canvas.saveState()
    # Header
    canvas.setFillColor(colors.HexColor(PRIMARY_COLOR))
    canvas.setFont("Helvetica-Bold", 10)
    # Adjusted position due to sidebar
    canvas.drawString(2.5*cm, PAGE_HEIGHT - 2*cm, REPORT_TITLE) 
    
    # Separator line (Header) - now Burnt Orange
    canvas.setStrokeColor(colors.HexColor(CONTRAST_COLOR))
    canvas.setLineWidth(1.5) # Thicker line
    canvas.line(2.5*cm, PAGE_HEIGHT - 2.2*cm, PAGE_WIDTH - 2*cm, PAGE_HEIGHT - 2.2*cm)

    # Footer - page number & small note
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor(PRIMARY_COLOR))
    page_num_text = f"Page {canvas.getPageNumber()}"
    canvas.drawRightString(PAGE_WIDTH - 2*cm, 1.4*cm, page_num_text)

    # Separator line (Footer - slightly above text) - now Burnt Orange
    canvas.setStrokeColor(colors.HexColor(CONTRAST_COLOR))
    canvas.setLineWidth(1.5) # Thicker line
    canvas.line(2.5*cm, 1.8*cm, PAGE_WIDTH - 2*cm, 1.8*cm)

    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2.5*cm, 1.4*cm, "Generated by PsyMitrix AI Engine | Confidential Profile")
    canvas.restoreState()

def _create_chart_guide_table(data):
    styles = getSampleStyleSheet()
    # Ensure a basic style is available for wrapping
    if "BodyText" not in styles:
        styles.add(ParagraphStyle(name="BodyText", fontName='Helvetica', fontSize=10, leading=12))

    # Wrap content in Paragraphs for auto line-breaks and bolding
    wrapped_data = [
        [Paragraph(str(cell), styles["BodyText"]) for cell in row]
        for row in data
    ]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(SECONDARY_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(PRIMARY_COLOR)),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor(ACCENT_COLOR)]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ])

    # Adjusted colWidths to handle wrapping
    table = Table(wrapped_data, colWidths=[100, 350], hAlign='LEFT')
    table.setStyle(style)
    return table

# ---------------------------
# Main PDF builder
# ---------------------------
def generate_personality_pdf(filename, data, person_name="Parth"):
    
    # 1. Generate all charts and logo into in-memory buffers
    # logo_buffer = make_placeholder_logo()
    logo_buffer = './psy.png'
    radar_buffer = create_radar_chart(data["sections"]["charts"]["radarChart"]["data"])
    bar_buffer = create_bar_chart(data["sections"]["charts"]["barChart"]["data"], title="Core Attribute Summary")
    cognitive_bar_buffer = create_bar_chart(
        data["sections"]["cognitive_scores"]["barChart"]["data"], 
        title="Cognitive Score Summary" 
    )
    comparison_bar_buffer = create_comparison_bar_chart(data["sections"]["charts"]["comparisonTable"]["data"])


    # Document setup
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=2.5*cm, # Increased left margin for vertical text
        rightMargin=2*cm,
        topMargin=2.6*cm,
        bottomMargin=2.2*cm,
        title=f"{person_name} - Personality Report"
    )

    styles = getSampleStyleSheet()
    # Fancier Styles
    styles.add(ParagraphStyle(name="ReportTitle", alignment=1, fontSize=30, textColor=colors.HexColor(TITLE_COLOR), spaceAfter=20, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="ReportSubtitle", alignment=1, fontSize=14, textColor=colors.HexColor(PRIMARY_COLOR), spaceAfter=30, fontName="Helvetica"))
    styles.add(ParagraphStyle(name="SectionHeader", fontSize=16, textColor=colors.HexColor(PRIMARY_COLOR), spaceAfter=10, spaceBefore=20, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="TraitTitle", fontSize=12, textColor=colors.HexColor(TITLE_COLOR), spaceAfter=4, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="Body", fontSize=10, leading=16, textColor=colors.HexColor("#333333"), fontName="Helvetica"))
    
    # FIX: Renamed 'Bullet' to 'CustomBullet' to avoid KeyError, as 'Bullet' is pre-defined.
    styles.add(ParagraphStyle(name="CustomBullet", parent=styles["Body"], leftIndent=0.5*cm, firstLineIndent=-0.5*cm))
    
    story = []

    # ----- COVER (Page 1) -----
    story.append(Spacer(1, 6*cm))
    story.append(RLImage(logo_buffer, width=4.5*cm, height=4.5*cm, hAlign='CENTER')) # Use buffer
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph(f"The Individual Profile of", styles["ReportSubtitle"]))
    story.append(Paragraph(f"<b>{person_name}</b>", styles["ReportTitle"]))
    story.append(Paragraph("Comprehensive Personality & Cognitive Profile", styles["ReportSubtitle"]))
    story.append(Paragraph(f"Generated on: <b>{datetime.now().strftime('%B %d, %Y')}</b>", styles["Body"]))
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("Confidential — For recipient only.", styles["Body"]))
    story.append(PageBreak())

    # ----- TABLE OF CONTENTS (Page 2) -----
    story.append(Paragraph("Table of Contents", styles["ReportTitle"]))
    story.append(Spacer(1, 0.5*cm))
    
    toc_data = [
        ["1.", "Report Overview", 3],
        ["2.", "How to Read This Report", 4],
        ["3.", "Understanding Your Results", 5],
        ["4.", "Personality Breakdown", 6],
        ["5.", "Cognitive Profile Overview", 7],
        ["6.", "Radar Chart of Traits", 8],
        ["7.", "Bar Chart Summary (Core Attributes)", 9],
        ["8.", "Cognitive Score Chart", 10],
        ["9.", "Trait Comparison Chart", 11],
        ["10.", "Career Fit Recommendations", 12],
        ["11.", "Next Steps", 13],
    ]
    
    toc_table_data = [[f"{row[0]}", row[1], f".... {row[2]}"] for row in toc_data]
    toc_table = Table(toc_table_data, colWidths=[30, 420, 50])
    toc_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor(TITLE_COLOR)),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.HexColor(SECONDARY_COLOR)),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # --- STATIC CONTENT PAGES ---

    # ----- 1. Report Overview (Page 3) -----
    story.append(Paragraph("1. Report Overview", styles["SectionHeader"]))
    overview_text = (
        "This <b>confidential report</b> summarizes your core personality, cognitive style, and motivational drivers. "
        "It is structured to provide an easy-to-digest profile for both personal growth and professional development. "
        "The subsequent sections will detail your traits, compare them against a general population benchmark, "
        "and provide actionable insights based on your unique profile."
    )
    story.append(Paragraph(overview_text, styles["Body"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Key Components:", styles["TraitTitle"]))
    key_components = [
        "Trait Breakdown: In-depth descriptions of how your major personality traits manifest.",
        "Graphical Summaries: Visual comparisons (Radar and Bar charts) for quick comprehension.",
        "Comparison Matrix: Benchmarking your scores against population averages.",
        "Recommendations: Practical advice for leveraging strengths and managing growth areas."
    ]
    for p in key_components:
        story.append(Paragraph("• " + p, styles["CustomBullet"]))
    story.append(PageBreak())

    # ----- 2. How to Read This Report (Page 4) -----
    story.append(Paragraph("2. How to Read This Report", styles["SectionHeader"]))
    story.append(Paragraph(
        "Understanding the scoring system and terminology is crucial for maximizing the value of this report. "
        "Each score reflects the intensity of the corresponding trait, interpreted along a standardized 1–10 scale.",
        styles["Body"]
    ))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Score Interpretation (1–10 Scale)", styles["TraitTitle"]))

    # FIX: Use Paragraphs inside table for text wrapping (Resolves table overflow)
    score_table_data = [
        [
            Paragraph("<b>Score Range</b>", styles["Body"]),
            Paragraph("<b>Interpretation</b>", styles["Body"]),
            Paragraph("<b>Meaning</b>", styles["Body"])
        ],
        [
            Paragraph("1 – 3", styles["Body"]),
            Paragraph("Low", styles["Body"]),
            Paragraph(
                "The trait is less dominant in your personality. For example, low Extraversion indicates introverted tendencies.",
                styles["Body"]
            )
        ],
        [
            Paragraph("4 – 6", styles["Body"]),
            Paragraph("Balanced / Moderate", styles["Body"]),
            Paragraph(
                "Represents flexibility. You can exhibit the trait when needed but maintain balance. This is typically the benchmark range.",
                styles["Body"]
            )
        ],
        [
            Paragraph("7 – 10", styles["Body"]),
            Paragraph("High", styles["Body"]),
            Paragraph(
                "This trait strongly defines your behavior and preferences. For instance, high Openness reflects curiosity, imagination, and creativity.",
                styles["Body"]
            )
        ],
    ]

    # FIX: Adjusted colWidths to fit within A4 margins (approx 480 points usable width)
    score_table = Table(score_table_data, colWidths=[70, 100, 300], repeatRows=1) 
    score_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 6),

        # Body text
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEADING', (0, 1), (-1, -1), 13),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # Alternate row background
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor(ACCENT_COLOR), colors.white]),

        # Borders & grid
        ('BOX', (0, 0), (-1, -1), 0.7, colors.HexColor(PRIMARY_COLOR)),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor(SECONDARY_COLOR)),

        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))

    story.append(score_table)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        f"<font color='{PRIMARY_COLOR}'><b>Tip:</b></font> Higher scores indicate stronger expression of that trait, "
        "but balance across dimensions is ideal for emotional and behavioral adaptability.",
        styles["Body"]
    ))
    # Removed redundant bullet point insertion here
    story.append(PageBreak())

    # ----- 3. Understanding Your Results (Page 5) -----
    story.append(Paragraph("3. Understanding Your Results", styles["SectionHeader"]))
    story.append(Paragraph(
        "Your personality profile is not a fixed label but a map of your current tendencies, providing clarity on how you process information, manage stress, and interact with the world. "
        "Use this report for self-awareness and targeted development, remembering that motivation and environment can always influence behavior.",
        styles["Body"]
    ))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Making the Most of Your Profile:", styles["TraitTitle"]))
    
    # FIX: Corrected escaped HTML tags to proper reportlab-compatible tags (<b>)
    reflection_points = [
        "Identify your <b>Core Strengths</b>: Which high-scoring traits align with your proudest accomplishments? Plan how to use them more intentionally.",
        "Acknowledge <b>Growth Areas</b>: Scores below 5 often suggest opportunities. Instead of viewing them as flaws, treat them as skills to be developed when needed.",
        "Reflect on <b>Context</b>: Does your report resonate with how you act at work, or at home? Understanding context is key to applying these insights.",
    ]
    for p in reflection_points:
        story.append(Paragraph("• " + p, styles["CustomBullet"]))
    story.append(PageBreak())


    # --- CORE REPORT CONTENT ---

    # ----- 4. Personality Breakdown (Page 6) -----
    story.append(Paragraph("4. Personality Breakdown", styles["SectionHeader"]))
    report_section = data["sections"]["report"]
    for trait, desc in report_section.items():
        story.append(KeepTogether([
            Paragraph(trait, styles["TraitTitle"]),
            Paragraph(desc, styles["Body"]),
            Spacer(1, 0.3*cm)
        ]))
    story.append(PageBreak())

    # ----- 5. Cognitive Profile Overview (Page 7) -----
    story.append(Paragraph("5. Cognitive Profile Overview", styles["SectionHeader"]))
    cognitive_intro = (
        "This section details your cognitive functioning, including key measures of aptitude and processing style. "
        "High scores indicate areas where you demonstrate speed and accuracy in mental tasks, while lower scores may point to preference differences in processing. "
        "The following chart visualizes your performance across core cognitive domains."
    )
    story.append(Paragraph(cognitive_intro, styles["Body"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(PageBreak())


    # ----- 6. Radar Chart of Traits (Page 8) -----
    radar_guide_data = [
        ['Element', 'Description'],
        ['Axes', 'Each axis represents a different personality trait.'],
        ['Value', 'The further the point is from the center, the higher the score in that trait.'],
    ]
    story.append(KeepTogether([
        Paragraph("6. Radar Chart of Traits", styles["SectionHeader"]),
        Paragraph(data["sections"]["charts"]["radarChart"]["explanation"], styles["Body"]),
        Spacer(1, 0.5*cm),
        RLImage(radar_buffer, width=12*cm, height=12*cm, hAlign='CENTER'), # Use buffer
        Spacer(1, 0.5*cm),
        Paragraph("How to Read This Chart", styles["TraitTitle"]),
        _create_chart_guide_table(radar_guide_data)
    ]))
    story.append(PageBreak())

    # ----- 7. Bar Chart Summary (Core Attributes) (Page 9) -----
    bar_guide_data = [
        ['Element', 'Description'],
        ['Bars', 'Each horizontal bar represents a core attribute.'],
        ['Length', 'The length of the bar corresponds to your score (0-100) in that area.'],
    ]
    story.append(KeepTogether([
        Paragraph("7. Bar Chart Summary (Core Attributes)", styles["SectionHeader"]),
        Paragraph(data["sections"]["charts"]["barChart"]["explanation"], styles["Body"]),
        Spacer(1, 0.5*cm),
        RLImage(bar_buffer, width=14*cm, height=7*cm, hAlign='CENTER'), # Use buffer
        Spacer(1, 0.5*cm),
        Paragraph("How to Read This Chart", styles["TraitTitle"]),
        _create_chart_guide_table(bar_guide_data)
    ]))
    story.append(PageBreak())

    # ----- 8. Cognitive Score Chart (New Chart Page 10) -----
    cognitive_guide_data = [
        ['Element', 'Description'],
        ['Bars', 'Each horizontal bar represents a cognitive ability.'],
        ['Length', 'The length of the bar shows your score in that cognitive domain.'],
    ]
    story.append(KeepTogether([
        Paragraph("8. Cognitive Score Chart", styles["SectionHeader"]),
        Paragraph(data["sections"]["cognitive_scores"]["barChart"]["explanation"], styles["Body"]),
        Spacer(1, 0.5*cm),
        RLImage(cognitive_bar_buffer, width=14*cm, height=7*cm, hAlign='CENTER'), # Use buffer
        Spacer(1, 0.5*cm),
        Paragraph("How to Read This Chart", styles["TraitTitle"]),
        _create_chart_guide_table(cognitive_guide_data)
    ]))
    story.append(PageBreak())

    # ----- 9. Comparison of Traits (Chart Page 11) -----
    comparison_guide_data = [
        ['Element', 'Description'],
        ['Your Score', 'The dark bar representing your score in a specific trait.'],
        ['Benchmark', 'The lighter bar representing the population average (5.0).'],
    ]
    story.append(KeepTogether([
        Paragraph("9. Trait Comparison Chart", styles["SectionHeader"]),
        Paragraph("The following chart benchmarks your core trait scores against the average population benchmark (Score of 5).", styles["Body"]),
        Spacer(1, 0.3*cm),
        RLImage(comparison_bar_buffer, width=16*cm, height=8*cm, hAlign='CENTER'), # Use buffer
        Spacer(1, 0.4*cm),
        Paragraph(data["sections"]["charts"]["comparisonTable"].get("explanation", ""), styles["Body"]),
        Spacer(1, 0.5*cm),
        Paragraph("How to Read This Chart", styles["TraitTitle"]),
        _create_chart_guide_table(comparison_guide_data)
    ]))
    story.append(PageBreak())
    
    # ----- 10. Career Fit Recommendations (Page 12) -----
    story.append(Paragraph("10. Career Fit Recommendations", styles["SectionHeader"]))
    story.append(Paragraph("These recommendations synthesize your strongest traits (Personality) and aptitudes (Cognitive) to suggest environments and roles where you are likely to thrive and find maximum engagement.", styles["Body"]))
    story.append(Spacer(1, 0.3*cm))
    
    insights = [
        "<b>Strengths Leverage:</b> Utilize high openness and strong logical reasoning by engaging in roles that require creativity and analytical problem-solving.",
        "<b>Growth Areas Focus:</b> Target spontaneous engagement and social energy development through varied networking opportunities to enhance broader team leadership capabilities.",
        "<b>Optimal Career Fit:</b> Analytical and structured roles (e.g., data analysis, QA engineering, project coordination) are best suited, leveraging the preference for methodical planning and clear objectives.",
        "<b>Ideal Environment:</b> Seek environments that provide clear goals, autonomy in execution, and value the delivery of high-quality, precise work over rapid, high-volume output."
    ]
    for p in insights:
        story.append(Paragraph("• " + p, styles["CustomBullet"]))
        story.append(Spacer(1, 0.15*cm))
    story.append(PageBreak())

    # ----- 11. Next Steps (Page 13) -----
    story.append(Paragraph("11. Next Steps", styles["SectionHeader"]))
    story.append(Paragraph(
        "Turning insight into action requires a concrete plan. Use these steps to integrate your profile results into your personal and professional development goals.",
        styles["Body"]
    ))
    story.append(Spacer(1, 0.5*cm))
    
    next_steps_list = [
        "<b>Discuss & Validate</b>: Share this report with a trusted mentor, coach, or manager to gain external perspective on how your traits align with observed behavior.",
        "<b>Set a SMART Goal</b>: Choose one of the identified 'Growth Areas' (e.g., Introversion–Extraversion) and set a specific, measurable goal for the next 90 days related to that area.",
        "<b>Track Success</b>: Document instances where your strengths helped you succeed and where your growth areas presented challenges. This reinforces self-awareness.",
        "<b>Revisit in Six Months</b>: Personal development is cyclical. Look back at this report to measure how your self-perception has evolved and to recalibrate your focus."
    ]
    for p in next_steps_list:
        story.append(Paragraph("• " + p, styles["CustomBullet"]))
        story.append(Spacer(1, 0.15*cm))


    # Build PDF with header/footer callbacks
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


# ---------------------------
# Example data (from your JSON) - unchanged
# ---------------------------
if __name__ == "__main__":
    data = {
      "sections": {
        "report": {
            "Openness": "Parth demonstrates a keen curiosity and appreciates new ideas, often seeking fresh experiences while valuing structure. He balances imaginative thinking with a practical approach, enabling him to explore innovative solutions without losing focus on execution.",
            "Individualization": "He exhibits a nuanced sensitivity towards others, recognizing unique traits and tailoring interactions accordingly. This attentiveness fosters rapport and collaboration, especially within his peer group, and allows him to navigate social dynamics with ease.",
            "Introversion–Extraversion": "Parth shows a preference for quiet reflection, yet he engages confidently in group settings when needed. His energy is best replenished through solitary activities, though he maintains an approachable demeanor in collaborative environments.",
            "Self-Esteem": "He possesses a steady sense of self-worth, grounded in consistent personal achievements. Confidence arises from his reliable performance rather than external validation, encouraging autonomy in decision-making.",
            "Enneagram & DISC Summary": "Parth aligns with a thoughtful, conscientious profile, emphasizing diligence and precision. His communication style reflects a calm, methodical tone, preferring clarity and thoroughness in exchanges.",
            "FIRO-B Summary": "He balances inclusion with independence, valuing close connections yet maintaining personal space. His focus on contribution encourages supportive teamwork while safeguarding personal boundaries.",
            "Career Fit": "His strengths point toward roles that demand analytical rigor and collaborative problem-solving, such as data analysis, quality assurance, or project coordination. Positions offering clear goals and structured environments will support his growth.",
            "Neuro Map": "Parth’s cognitive profile highlights strong logical processing and a preference for methodical planning. Emotional regulation is achieved through routine and clear expectations, ensuring stability in dynamic situations."
          },
          "charts": {
            "radarChart": {
              "data": [
                {"field": "Openness", "value": 8},
                {"field": "Individualization", "value": 7},
                {"field": "Introversion–Extraversion", "value": 4},
                {"field": "Self-Esteem", "value": 6},
                {"field": "Enneagram&DISC", "value": 5}
              ],
              "explanation": "The radar chart illustrates Parth’s balanced orientation, showing high openness, strong individualization, moderate self-esteem, and a preference for introspection, with consistent conscientious traits."
            },
            "barChart": {
              "data": [
                {"field": "Strengths", "value": 9},
                {"field": "Weaknesses", "value": 4},
                {"field": "GrowthAreas", "value": 7},
                {"field": "Motivation", "value": 8},
                {"field": "Interaction", "value": 6}
              ],
              "explanation": "The bar chart displays Parth’s key attributes: top strengths in logical analysis, moderate weaknesses in spontaneous engagement, solid growth potential, high motivation, and solid interaction skills."
            },
            "comparisonTable": {
              "data": [
                {"field": "Openness", "value": 8},
                {"field": "Introversion", "value": 4},
                {"field": "SelfEsteem", "value": 6},
                {"field": "EnneagramScore", "value": 5}
              ],
              "explanation": "The comparison table contrasts Parth’s scores with typical benchmarks, indicating above-average openness, lower introversion, solid self-esteem, and a moderate conscientious profile."
            }
          },
            "cognitive_scores": {
                "barChart": {
                    "data": [
                        {"field": "Logical Reasoning", "value": 9},
                        {"field": "Verbal Comprehension", "value": 7},
                        {"field": "Working Memory", "value": 6},
                        {"field": "Processing Speed", "value": 5}
                    ],
                    "explanation": "This chart summarizes Parth’s cognitive abilities, highlighting strong Logical Reasoning and solid Verbal Comprehension, supporting an analytical profile. Working Memory is efficient, while Processing Speed is within the typical range."
                }
            }
        }
    }

    generate_personality_pdf("Parth_Personality_Report_Fancier_V4.pdf", data, person_name="Parth")
