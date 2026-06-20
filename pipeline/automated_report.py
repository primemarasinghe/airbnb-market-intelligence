"""
Automated Weekly Market Intelligence Report
Using ReportLab for professional PDF generation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, Image, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.pdfgen import canvas as rl_canvas
import warnings
warnings.filterwarnings("ignore")

# Load data
df = pd.read_csv("data/processed/listings_enriched.csv", low_memory=False)
reviews = pd.read_csv("data/processed/reviews_clean.csv", low_memory=False)
df["occupancy_rate"] = 1 - (df["availability_365"] / 365)
df["estimated_annual_revenue"] = df["price"] * (365 - df["availability_365"])
df_clean = df[df["price"].between(100, 10000)].copy()
reviews["date"] = pd.to_datetime(reviews["date"])

# Colors
DARK_BLUE = colors.HexColor("#1F3864")
MED_BLUE = colors.HexColor("#2E75B6")
LIGHT_BLUE = colors.HexColor("#D6E4F0")
CYAN = colors.HexColor("#00d4ff")
GREEN = colors.HexColor("#4ade80")
RED = colors.HexColor("#ff6b6b")
ORANGE = colors.HexColor("#f59e0b")
GRAY = colors.HexColor("#7a8499")
LIGHT_GRAY = colors.HexColor("#f8f9fa")
WHITE = colors.white
BLACK = colors.black

def make_chart(fig):
    """Convert matplotlib figure to ReportLab Image"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white")
    buf.seek(0)
    plt.close(fig)
    return buf

def header_footer(canvas, doc):
    """Add header and footer to every page"""
    canvas.saveState()
    w, h = A4

    # Header bar
    canvas.setFillColor(DARK_BLUE)
    canvas.rect(0, h - 20*mm, w, 20*mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(15*mm, h - 13*mm, "BANGKOK AIRBNB MARKET INTELLIGENCE")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w - 15*mm, h - 13*mm,
                           f"Generated: {datetime.now().strftime('%B %d, %Y')}")

    # Cyan accent line
    canvas.setFillColor(CYAN)
    canvas.rect(0, h - 22*mm, w, 2*mm, fill=1, stroke=0)

    # Footer
    canvas.setFillColor(LIGHT_GRAY)
    canvas.rect(0, 0, w, 12*mm, fill=1, stroke=0)
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(15*mm, 4*mm,
                      "Prepared by: Primesh Marasinghe | SLIIT BSc Data Science | Expernetic Data Engineer Assessment")
    canvas.drawRightString(w - 15*mm, 4*mm, f"Page {doc.page}")

    canvas.restoreState()

# Styles
styles = getSampleStyleSheet()

title_style = ParagraphStyle("title", fontSize=28, fontName="Helvetica-Bold",
                              textColor=WHITE, alignment=TA_CENTER, spaceAfter=6)
subtitle_style = ParagraphStyle("subtitle", fontSize=13, fontName="Helvetica",
                                 textColor=colors.HexColor("#a0b8d0"),
                                 alignment=TA_CENTER, spaceAfter=4)
h1_style = ParagraphStyle("h1", fontSize=16, fontName="Helvetica-Bold",
                           textColor=DARK_BLUE, spaceBefore=12, spaceAfter=6,
                           borderPad=4)
h2_style = ParagraphStyle("h2", fontSize=12, fontName="Helvetica-Bold",
                           textColor=MED_BLUE, spaceBefore=8, spaceAfter=4)
body_style = ParagraphStyle("body", fontSize=9, fontName="Helvetica",
                             textColor=BLACK, spaceAfter=4, leading=14)
insight_style = ParagraphStyle("insight", fontSize=9, fontName="Helvetica-Oblique",
                                textColor=colors.HexColor("#1F3864"),
                                backColor=LIGHT_BLUE, borderPad=6,
                                spaceAfter=8, leading=13,
                                leftIndent=8, rightIndent=8)
bullet_style = ParagraphStyle("bullet", fontSize=9, fontName="Helvetica",
                               textColor=BLACK, spaceAfter=3, leading=13,
                               leftIndent=12, bulletIndent=4)

def kpi_table(data):
    """Create a KPI metrics table"""
    t = Table(data, colWidths=[42*mm]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), CYAN),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 18),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#2a3550")),
        ("TEXTCOLOR", (0,1), (-1,1), colors.HexColor("#a0b8d0")),
        ("FONTNAME", (0,1), (-1,1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,1), 8),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [DARK_BLUE, colors.HexColor("#2a3550")]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#3a4560")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t

def section_header(title, subtitle=""):
    elems = []
    elems.append(Spacer(1, 4*mm))
    elems.append(HRFlowable(width="100%", thickness=2, color=MED_BLUE))
    elems.append(Paragraph(title, h1_style))
    if subtitle:
        elems.append(Paragraph(subtitle, ParagraphStyle("sh", fontSize=9,
                               textColor=GRAY, spaceAfter=8, fontName="Helvetica-Oblique")))
    return elems

# Build PDF
OUTPUT = "report/Weekly_Market_Intelligence_Report.pdf"
doc = BaseDocTemplate(OUTPUT, pagesize=A4,
                       leftMargin=15*mm, rightMargin=15*mm,
                       topMargin=28*mm, bottomMargin=18*mm)

frame = Frame(doc.leftMargin, doc.bottomMargin,
              doc.width, doc.height, id="main")
template = PageTemplate(id="main", frames=frame,
                         onPage=header_footer)
doc.addPageTemplates([template])

story = []

# ============ PAGE 1: COVER ============
# Dark cover background via drawing
story.append(Spacer(1, 15*mm))

# Cover box
cover_data = [
    [Paragraph("BANGKOK AIRBNB", ParagraphStyle("ct", fontSize=32,
               fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER))],
    [Paragraph("Market Intelligence Report", ParagraphStyle("cs", fontSize=18,
               fontName="Helvetica", textColor=CYAN, alignment=TA_CENTER))],
    [Paragraph(f"Weekly Edition · {datetime.now().strftime('%B %d, %Y')}",
               ParagraphStyle("cd", fontSize=11, fontName="Helvetica",
                              textColor=colors.HexColor("#a0b8d0"), alignment=TA_CENTER))],
]
cover_table = Table(cover_data, colWidths=[170*mm])
cover_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("TOPPADDING", (0,0), (-1,-1), 12),
    ("BOTTOMPADDING", (0,0), (-1,-1), 12),
    ("ROUNDEDCORNERS", [8]),
]))
story.append(cover_table)
story.append(Spacer(1, 8*mm))

# KPI metrics
kpi_data = [
    ["28,806", "฿1,359", "31.5%", "583,333"],
    ["Total Listings", "Median Price/Night", "Avg Occupancy", "Total Reviews"],
]
story.append(kpi_table(kpi_data))
story.append(Spacer(1, 6*mm))

kpi_data2 = [
    ["8,874", "50", "148,869", "57%"],
    ["Unique Hosts", "Neighbourhoods", "2024 Reviews (ATH)", "Commercial Supply"],
]
story.append(kpi_table(kpi_data2))
story.append(Spacer(1, 8*mm))

story.append(Paragraph(
    "This report provides a comprehensive analysis of the Bangkok short-term rental market "
    "based on Inside Airbnb data (September 2025 scrape). Findings cover pricing dynamics, "
    "host behavior, demand seasonality, and actionable business recommendations.",
    body_style))

story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "💡 Key Headline: Bangkok's Airbnb market has surpassed pre-COVID peaks by 152%, "
    "with 2024 recording an all-time high of 148,869 reviews. The market is dominated by "
    "commercial operators (57% of supply) and shows significant pricing opportunities "
    "in weekend premiums and amenity differentiation.",
    insight_style))

story.append(PageBreak())

# ============ PAGE 2: PRICING ANALYSIS ============
story.extend(section_header("1. Pricing & Supply Analysis",
    "Market-wide price distribution, room type premiums, and neighbourhood dynamics"))

# Price by room type chart
fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
fig.patch.set_facecolor("white")

room_price = df_clean.groupby("room_type")["price"].median().sort_values()
colors_list = ["#2E75B6", "#4ade80", "#f59e0b", "#ff6b6b"]
bars = axes[0].barh(room_price.index, room_price.values, color=colors_list)
axes[0].set_title("Median Price by Room Type (THB)", fontweight="bold", color="#1F3864")
axes[0].set_xlabel("Median Price (฿)")
for bar, val in zip(bars, room_price.values):
    axes[0].text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                 f"฿{val:,.0f}", va="center", fontsize=8, color="#1F3864")

top_nb = df_clean.groupby("neighbourhood_cleansed")["price"].median().sort_values(ascending=False).head(10)
axes[1].barh(top_nb.index[::-1], top_nb.values[::-1], color="#2E75B6")
axes[1].set_title("Top 10 Neighbourhoods by Median Price", fontweight="bold", color="#1F3864")
axes[1].set_xlabel("Median Price (฿)")
plt.tight_layout()

buf = make_chart(fig)
story.append(Image(buf, width=170*mm, height=60*mm))
story.append(Spacer(1, 3*mm))

# Pricing insights table
price_table_data = [
    ["Metric", "Value", "Business Insight"],
    ["Market Median Price", "฿1,359/night", "Affordable vs global markets (~$38 USD)"],
    ["Entire Home Premium", "+38% vs Private Room", "Statistically significant (p<0.0001, r=0.29)"],
    ["Most Expensive Area", "Parthum Wan ฿2,225", "Premium CBD positioning"],
    ["Most Affordable Area", "Nong Khaem ฿581", "Outer district, lower tourist density"],
    ["Price Range", "฿100 – ฿10,000+", "Long tail luxury segment (8% of market)"],
    ["Outliers", "Max ฿1,000,000", "Likely data entry errors — flagged in pipeline"],
]
pt = Table(price_table_data, colWidths=[50*mm, 50*mm, 70*mm])
pt.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
    ("TEXTCOLOR", (0,0), (-1,0), WHITE),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d0d8e0")),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
story.append(pt)
story.append(Spacer(1, 3*mm))
story.append(Paragraph(
    "💡 Investment Insight: Neighbourhood explains 10.5% of price variance (η²=0.1055, p<0.0001). "
    "Bang Rak and Vadhana offer the best combination of pricing power and market liquidity.",
    insight_style))

story.append(PageBreak())

# ============ PAGE 3: HOST & DEMAND ============
story.extend(section_header("2. Host Analysis & Demand Dynamics",
    "Host segmentation, superhost impact, and booking demand patterns"))

# Host analysis charts
fig, axes = plt.subplots(1, 3, figsize=(14, 3.5))
fig.patch.set_facecolor("white")

# Host type pie
host_counts = df_clean["host_type"].value_counts()
axes[0].pie(host_counts.values, labels=host_counts.index,
            autopct="%1.1f%%", colors=["#2E75B6", "#4ade80", "#ff6b6b"],
            startangle=90, textprops={"fontsize": 8})
axes[0].set_title("Host Market Structure", fontweight="bold", color="#1F3864")

# Superhost comparison
sh_labels = ["Non-Superhost", "Superhost"]
ratings = [4.575, 4.858]
revenues = [25968, 114431]
x = np.arange(2)
ax2b = axes[1].twinx()
bars1 = axes[1].bar(x - 0.2, ratings, 0.35, color="#2E75B6", label="Avg Rating", alpha=0.8)
bars2 = ax2b.bar(x + 0.2, revenues, 0.35, color="#4ade80", label="Annual Revenue", alpha=0.8)
axes[1].set_xticks(x)
axes[1].set_xticklabels(sh_labels, fontsize=8)
axes[1].set_ylabel("Avg Rating", color="#2E75B6", fontsize=8)
ax2b.set_ylabel("Annual Revenue (฿)", color="#4ade80", fontsize=8)
axes[1].set_ylim(4.0, 5.2)
axes[1].set_title("Superhost vs Non-Superhost", fontweight="bold", color="#1F3864")
axes[1].legend(loc="upper left", fontsize=7)
ax2b.legend(loc="upper right", fontsize=7)

# Monthly review volume
monthly = reviews[reviews["date"].dt.year.between(2019, 2025)].groupby(
    reviews["date"].dt.to_period("M")).size().reset_index()
monthly.columns = ["period", "count"]
monthly["date"] = monthly["period"].dt.to_timestamp()
axes[2].fill_between(monthly["date"], monthly["count"], alpha=0.3, color="#2E75B6")
axes[2].plot(monthly["date"], monthly["count"], color="#2E75B6", linewidth=1.5)
axes[2].axvline(pd.Timestamp("2020-03-01"), color="#ff6b6b", linestyle="--", alpha=0.7)
axes[2].set_title("Monthly Review Volume (Demand)", fontweight="bold", color="#1F3864")
axes[2].set_ylabel("Reviews", fontsize=8)
axes[2].tick_params(axis="x", rotation=30, labelsize=7)
plt.tight_layout()

buf = make_chart(fig)
story.append(Image(buf, width=170*mm, height=60*mm))
story.append(Spacer(1, 3*mm))

# Host segment table
host_table_data = [
    ["Host Segment", "Count", "Avg Price", "Occupancy", "Avg Rating", "Key Characteristic"],
    ["High Occupancy", "1,085", "฿1,573", "61.0%", "4.81", "Best revenue efficiency"],
    ["Casual Hosts", "2,122", "฿1,305", "14.0%", "4.75", "Single/few listings"],
    ["Luxury Hosts", "406", "฿4,715", "18.0%", "4.79", "Premium pricing strategy"],
    ["Commercial Ops", "69", "฿1,678", "15.0%", "4.56", "58.9 listings avg — lowest rated"],
    ["Professional Multi", "53", "฿1,774", "31.0%", "4.76", "28.6 listings, 2,564 reviews avg"],
    ["Long-Stay Specs", "29", "฿1,401", "17.0%", "4.67", "179-night minimum avg"],
]
ht = Table(host_table_data, colWidths=[32*mm, 18*mm, 22*mm, 22*mm, 22*mm, 54*mm])
ht.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
    ("TEXTCOLOR", (0,0), (-1,0), WHITE),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("ALIGN", (0,0), (0,-1), "LEFT"),
    ("ALIGN", (-1,0), (-1,-1), "LEFT"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d0d8e0")),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 4),
]))
story.append(ht)
story.append(Spacer(1, 3*mm))
story.append(Paragraph(
    "💡 Key Finding: Superhosts earn 340% more annual revenue (฿114,431 vs ฿25,968) "
    "not through higher prices (only ฿19 difference) but through higher occupancy and "
    "stronger guest ratings (Cohen's d=0.54, medium effect size).",
    insight_style))

story.append(PageBreak())

# ============ PAGE 4: STATISTICAL FINDINGS ============
story.extend(section_header("3. Statistical Analysis & ML Results",
    "Formal hypothesis tests, effect sizes, and predictive model performance"))

# Hypothesis table
hyp_data = [
    ["Hypothesis", "Test Used", "P-value", "Effect Size", "Practical Impact", "Decision"],
    ["H1: Entire home > Private room price",
     "Mann-Whitney U", "p<0.0001", "r=0.29 (moderate)", "38% price premium", "REJECT H0"],
    ["H2: Superhost > Non-superhost rating",
     "Mann-Whitney U", "p<0.0001", "d=0.54 (medium)", "0.28 point gap", "REJECT H0"],
    ["H3: >10 reviews affects price",
     "Mann-Whitney U", "p=0.000005", "r=0.037 (negligible)", "฿41 difference only", "REJECT H0*"],
    ["H4: Neighbourhood price differences",
     "Kruskal-Wallis", "p<0.0001", "n2=0.105 (moderate)", "81% price range", "REJECT H0"],
    ["H5: Weekend vs weekday pricing",
     "Mann-Whitney U", "p=0.526", "d=0.012 (negligible)", "฿3 difference", "FAIL TO REJECT"],
]
ht2 = Table(hyp_data, colWidths=[42*mm, 28*mm, 18*mm, 26*mm, 26*mm, 26*mm])
ht2.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
    ("TEXTCOLOR", (0,0), (-1,0), WHITE),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 7.5),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d0d8e0")),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 4),
    ("BACKGROUND", (5,1), (5,1), colors.HexColor("#d4edda")),
    ("BACKGROUND", (5,2), (5,2), colors.HexColor("#d4edda")),
    ("BACKGROUND", (5,3), (5,3), colors.HexColor("#fff3cd")),
    ("BACKGROUND", (5,4), (5,4), colors.HexColor("#d4edda")),
    ("BACKGROUND", (5,5), (5,5), colors.HexColor("#f8d7da")),
]))
story.append(ht2)
story.append(Spacer(1, 3*mm))
story.append(Paragraph(
    "* H3 note: Statistically significant but effect size negligible (r=0.037). "
    "Large sample sizes (n=23,039) amplify trivial differences — effect sizes must always "
    "accompany p-values for credible statistical reporting.",
    body_style))
story.append(Spacer(1, 4*mm))

# ML results
story.append(Paragraph("Price Prediction Model Performance (5-Fold Cross-Validation)", h2_style))

fig, axes = plt.subplots(1, 2, figsize=(10, 3))
fig.patch.set_facecolor("white")

models = ["Ridge Regression", "Random Forest", "Gradient Boosting"]
maes = [655, 501, 504]
r2s = [0.449, 0.652, 0.662]
mapes = [42.1, 29.2, 29.1]
x = np.arange(3)

axes[0].bar(x, maes, color=["#ff6b6b", "#4ade80", "#2E75B6"])
axes[0].set_xticks(x)
axes[0].set_xticklabels(["Ridge", "Random\nForest", "Gradient\nBoosting"], fontsize=8)
axes[0].set_title("MAE by Model (฿)", fontweight="bold", color="#1F3864")
axes[0].set_ylabel("MAE (฿)")
for i, v in enumerate(maes):
    axes[0].text(i, v + 10, f"฿{v:,}", ha="center", fontsize=8)

axes[1].bar(x, r2s, color=["#ff6b6b", "#4ade80", "#2E75B6"])
axes[1].set_xticks(x)
axes[1].set_xticklabels(["Ridge", "Random\nForest", "Gradient\nBoosting"], fontsize=8)
axes[1].set_title("R-Squared by Model", fontweight="bold", color="#1F3864")
axes[1].set_ylabel("R-Squared")
axes[1].set_ylim(0, 0.8)
for i, v in enumerate(r2s):
    axes[1].text(i, v + 0.01, f"{v:.3f}", ha="center", fontsize=8)
plt.tight_layout()

buf = make_chart(fig)
story.append(Image(buf, width=150*mm, height=55*mm))
story.append(Spacer(1, 3*mm))
story.append(Paragraph(
    "💡 ML Insight: Gradient Boosting wins (R2=0.662, MAE=฿504, MAPE=29.1%). "
    "Top price drivers: bedrooms (43.2%), neighbourhood median price (16.9%), "
    "accommodates (12.2%). Price is non-linear — Ridge regression (linear) "
    "performs significantly worse.",
    insight_style))

story.append(PageBreak())

# ============ PAGE 5: NLP & RECOMMENDATIONS ============
story.extend(section_header("4. NLP Insights & Business Recommendations",
    "Guest sentiment analysis, review themes, and actionable market recommendations"))

# NLP findings
story.append(Paragraph("Guest Review Intelligence (n=513,708 reviews)", h2_style))

nlp_data = [
    ["NLP Analysis", "Finding", "Business Implication"],
    ["Sentiment (VADER)", "72.9% Positive | 22.7% Neutral | 4.4% Negative",
     "High positivity consistent with rating inflation pattern"],
    ["Top Landmark", "BTS mentioned 2,513 times", "Transport proximity is #1 booking driver"],
    ["Top Amenity", "Pool mentioned 1,474 times", "Pool commands 19.6% price premium"],
    ["Top Complaint", "'Small' mentioned 679 times", "Room size is primary disappointment"],
    ["Language Mix", "40% non-English reviews (German, Spanish, French)",
     "English-only NLP misses 40% of sentiment signals"],
    ["Repeat Intent", "'Again' mentioned 5,631 times", "Strong loyalty signal — high rebooking rate"],
    ["Quality Classifier", "24.1% informative | 25.6% superficial",
     "1 in 4 reviews provides no actionable guest signal"],
    ["LDA Topics", "3 of 6 topics non-English", "Multilingual modeling required for production"],
]
nt = Table(nlp_data, colWidths=[38*mm, 60*mm, 72*mm])
nt.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
    ("TEXTCOLOR", (0,0), (-1,0), WHITE),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d0d8e0")),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 4),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
]))
story.append(nt)
story.append(Spacer(1, 5*mm))

# Recommendations
story.append(Paragraph("Business Recommendations", h2_style))

rec_data = [
    [Paragraph("<b>FOR HOSTS</b>", ParagraphStyle("rh", fontSize=9, fontName="Helvetica-Bold",
               textColor=WHITE)),
     Paragraph("<b>FOR INVESTORS</b>", ParagraphStyle("rh", fontSize=9, fontName="Helvetica-Bold",
               textColor=WHITE)),
     Paragraph("<b>FOR PLATFORM OPERATORS</b>", ParagraphStyle("rh", fontSize=9,
               fontName="Helvetica-Bold", textColor=WHITE))],
    [Paragraph(
        "• Pursue Superhost → +340% revenue<br/>"
        "• Weekend pricing premium (zero now)<br/>"
        "• Highlight BTS/MRT in listing title<br/>"
        "• Upgrade TV (+68.6% premium)<br/>"
        "• Dynamic pricing Jul–Sep peak",
        ParagraphStyle("rb", fontSize=8, fontName="Helvetica", leading=14)),
     Paragraph(
        "• Bang Rak / Vadhana for premium<br/>"
        "• Mid-market ฿1,000–2,500 sweet spot<br/>"
        "• 2024 at all-time high (+152% vs 2019)<br/>"
        "• High Demand segment: 61% occupancy<br/>"
        "• Avoid shared rooms (11.6% occupancy)",
        ParagraphStyle("rb", fontSize=8, fontName="Helvetica", leading=14)),
     Paragraph(
        "• Monitor commercial concentration (57%)<br/>"
        "• Address rating inflation (81.4% >4.5)<br/>"
        "• Multilingual review analysis needed<br/>"
        "• Regulatory risk mirrors Amsterdam<br/>"
        "• Weekend pricing tools for hosts",
        ParagraphStyle("rb", fontSize=8, fontName="Helvetica", leading=14))],
]
rt = Table(rec_data, colWidths=[56*mm, 56*mm, 58*mm])
rt.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
    ("TEXTCOLOR", (0,0), (-1,0), WHITE),
    ("BACKGROUND", (0,1), (-1,1), LIGHT_BLUE),
    ("GRID", (0,0), (-1,-1), 0.5, MED_BLUE),
    ("TOPPADDING", (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("ALIGN", (0,0), (-1,0), "CENTER"),
]))
story.append(rt)
story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "💡 Biggest Opportunity: Bangkok's zero weekend pricing premium represents an "
    "immediate revenue opportunity for early-adopter hosts. A 10–15% Friday-Saturday "
    "surcharge faces minimal competitive resistance given H5 confirms no current premium exists.",
    insight_style))

# Build
doc.build(story)
print(f"Report generated: {OUTPUT}")
print("Pages: Cover + Pricing & Supply + Host & Demand + Statistical & ML + NLP & Recommendations")