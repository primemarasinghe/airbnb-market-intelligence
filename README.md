# 🏙️ Bangkok Airbnb Market Intelligence

> End-to-end data engineering pipeline and market analysis on the Inside Airbnb 
> Bangkok dataset — built as part of the Expernetic Data Engineer Intern Assessment.

---

## 📊 Project Overview

This project transforms raw Inside Airbnb data into actionable market intelligence 
through a production-quality data pipeline, rigorous statistical analysis, and an 
interactive business dashboard.

**Dataset:** Inside Airbnb — Bangkok, Thailand (September 2025 Scrape)  
**Listings analyzed:** 28,806  
**Neighbourhoods:** 50  
**Reviews:** 583,333  

---

## 🏗️ Architecture
Raw Data → Ingestion → Profiling → Cleaning → Enrichment → Star Schema

↓

EDA + Hypothesis Testing

↓

Interactive Dashboard

---

## 📁 Repository Structure
airbnb-market-intelligence/

├── pipeline/

│   ├── ingest.py          # Data download with retry logic + metadata tracking

│   ├── profile.py         # Automated data profiling → JSON report

│   ├── clean.py           # Cleaning, standardization, validation flags

│   └── enrich.py          # Enrichment, occupancy, star schema construction

├── notebooks/

│   ├── 01_eda.ipynb       # Exploratory Data Analysis (9 visualizations)

│   └── 02_hypothesis_testing.ipynb  # 5 formal hypothesis tests

├── dashboard/

│   └── app.py             # Streamlit market intelligence dashboard

├── report/

│   └── Bangkok_Airbnb_Intelligence_Report.pdf

├── requirements.txt

└── README.md

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/primemarasinghe/airbnb-market-intelligence.git
cd airbnb-market-intelligence
pip install -r requirements.txt
```

### 2. Download Data
```bash
python pipeline/ingest.py
```
Downloads Bangkok dataset from Inside Airbnb automatically.

### 3. Process Data
```bash
python pipeline/profile.py   # Profile raw data
python pipeline/clean.py     # Clean and standardize
python pipeline/enrich.py    # Enrich and build star schema
```

### 4. Run Dashboard
```bash
streamlit run dashboard/app.py
```

### 5. Open Notebooks
```bash
jupyter notebook notebooks/
```

---

## 🔑 Key Findings

| Finding | Detail |
|---------|--------|
| Median nightly price | ฿1,383 THB (~$38 USD) |
| Market concentration | 57% of listings by commercial operators |
| Peak season | July–September (43% occupancy) |
| Superhost rating premium | +0.28 points (Cohen's d=0.54) |
| Post-COVID growth | 2024 reviews 152% above 2019 peak |
| Weekend price premium | None (p=0.526) — missed opportunity |

---

## 📈 Dashboard Features

- KPI metrics with live filter updates
- Price distribution by room type (violin plots)
- Neighbourhood supply and pricing analysis
- Host market structure (commercial vs casual)
- Interactive listing map (price heatmap)
- Market growth trend with COVID annotation
- Sidebar filters: room type, price range, neighbourhood, superhost

---

## 🧪 Hypothesis Tests

| Hypothesis | Result | Effect Size |
|-----------|--------|-------------|
| H1: Entire home > Private room price | REJECT H₀ | r=0.29 (moderate) |
| H2: Superhost > Non-superhost rating | REJECT H₀ | d=0.54 (medium) |
| H3: Reviews count affects price | REJECT H₀ | r=0.037 (negligible) |
| H4: Neighbourhood price differences | REJECT H₀ | η²=0.11 (moderate) |
| H5: Weekend vs weekday pricing | FAIL TO REJECT H₀ | d=0.012 (negligible) |

---

## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Data Processing:** pandas, numpy
- **Statistics:** scipy, statsmodels
- **Visualization:** plotly, matplotlib, seaborn
- **Dashboard:** Streamlit
- **Version Control:** Git + GitHub

---

## 📄 Report

Full analysis report available at `report/Bangkok_Airbnb_Intelligence_Report.pdf`

Sections covered:
1. Executive Summary
2. Objectives & Scope
3. Dataset Overview
4. Methodology
5. Engineering Approach
6. EDA Findings
7. Statistical Findings
8. Data Science Experiments (planned)
9. AI/ML Experiments
10. Visualizations
11. Business Recommendations
12. Cross-City Comparisons (planned)
13. Limitations & Caveats
14. Future Improvements
15. Reflection
- Appendix A: AI Usage Disclosure

---

## 🤖 AI Usage

AI tools (Claude Sonnet 4.6, GitHub Copilot) were used as productivity 
multipliers for code generation and report structuring. All outputs were 
independently verified, tested, and modified where necessary. Full 
disclosure in Appendix A of the report.

---

## 👤 Author

**Primesh Marasinghe**  
BSc (Hons) Data Science — SLIIT  
[GitHub](https://github.com/primemarasinghe)