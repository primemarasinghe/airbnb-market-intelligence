# 🏙️ Bangkok Airbnb Market Intelligence

> End-to-end data engineering pipeline and market analysis on the Inside Airbnb Bangkok dataset — built as part of the Expernetic Data Engineer Intern Assessment.

---

## 📊 Project Overview

This project transforms raw Inside Airbnb data into actionable market intelligence through a production-quality data pipeline, rigorous statistical analysis, machine learning models, NLP analysis, and an interactive business dashboard.

**Dataset:** Inside Airbnb — Bangkok, Thailand (September 2025 Scrape)  
**Listings analyzed:** 28,806  
**Neighbourhoods:** 50  
**Reviews:** 583,333  
**Calendar records:** 10,514,202  

---

## 🏗️ Architecture
Raw Data → Ingestion → Profiling → Cleaning → Enrichment → Star Schema

↓

DuckDB SQL Analytics

↓

EDA + Hypothesis Testing

OLS Regression + VIF

K-Means Clustering

ML Price Prediction

NLP Sentiment Analysis

RAG Q&A System

Demand Forecasting

Recommendation System

↓

Interactive Dashboard

---

## 📁 Repository Structure
airbnb-market-intelligence/

├── pipeline/

│   ├── ingest.py                  # Data download with retry + metadata

│   ├── profile.py                 # Automated data profiling

│   ├── clean.py                   # Cleaning + validation flags

│   ├── enrich.py                  # Enrichment + star schema

│   ├── sql_analytics.py           # DuckDB SQL analytical queries

│   ├── architecture_diagram.py    # Data pipeline diagram

│   └── cloud_architecture.py      # AWS cloud architecture diagram

├── notebooks/

│   ├── 01_eda.ipynb               # EDA (9 visualizations)

│   ├── 02_hypothesis_testing.ipynb # 5 tests + CI + OLS + VIF

│   ├── 03_ml_price_prediction.ipynb # 3 models + bias analysis

│   ├── 04_nlp_reviews.ipynb       # Sentiment + word frequency

│   ├── 05_clustering.ipynb        # K-Means (5 segments)

│   ├── 06_rag_system.ipynb        # RAG Q&A + Generative AI

│   ├── 07_demand_forecasting.ipynb # Trend + seasonality model

│   └── 08_recommendation_system.ipynb # Content-based filtering

├── dashboard/

│   └── app.py                     # Streamlit dashboard

├── tests/

│   └── test_pipeline.py           # 21 unit tests (all passing)

├── report/

│   ├── architecture_diagram.png

│   └── cloud_architecture.png

├── Dockerfile

├── docker-compose.yml

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

### 2. Download & Process Data
```bash
python pipeline/ingest.py
python pipeline/profile.py
python pipeline/clean.py
python pipeline/enrich.py
python pipeline/sql_analytics.py
```

### 3. Run Dashboard
```bash
streamlit run dashboard/app.py
streamlit run dashboard/ai_analyst.py
```

### 4. Run Tests
```bash
pytest tests/test_pipeline.py -v
```

### 5. Docker
```bash
docker-compose up
```

---

## 🔑 Key Findings

| Finding | Detail |
|---------|--------|
| Median nightly price | ฿1,383 THB (~$38 USD) |
| Market concentration | 57% of listings by commercial operators |
| Peak season | July–September (43% occupancy) |
| Superhost revenue premium | ฿114,431 vs ฿25,968 (340% gap) |
| Post-COVID growth | 2024 reviews 152% above 2019 peak |
| Weekend price premium | None (p=0.526) — missed opportunity |
| Best ML model | Gradient Boosting (R²=0.662, MAPE=29.1%) |
| Top price driver | Bedrooms (43.2% feature importance) |
| Sentiment | 72.9% positive reviews (VADER) |

---

## 🧪 Analysis Completed

| Section | Status |
|---------|--------|
| §02 Dataset Familiarization | ✅ Complete |
| §03.1 Ingestion & Profiling | ✅ Complete |
| §03.2 Cleaning & Standardization | ✅ Complete |
| §03.3 Enrichment & Joining | ✅ Complete |
| §03.4 Star Schema + DuckDB SQL | ✅ Complete |
| §03.5 Pipeline Automation | ✅ Complete |
| §04 EDA (5 subsections) | ✅ Complete |
| §05.1 Hypothesis Testing (H1-H5) | ✅ Complete |
| §05.2 Confidence Intervals | ✅ Complete |
| §05.3 OLS Regression + VIF | ✅ Complete |
| §06.1 ML Price Prediction | ✅ Complete |
| §06.2 Demand Forecasting | ✅ Complete |
| §06.3 K-Means Clustering | ✅ Complete |
| §06.4 Model Bias Analysis | ✅ Complete |
| §07.1 NLP Sentiment Analysis | ✅ Complete |
| §07.2 RAG Q&A System | ✅ Complete |
| §07.3 Recommendation System | ✅ Complete |
| §07.4 Generative AI Framework | ✅ Complete |
| §08 Interactive Dashboard | ✅ Complete |
| Unit Tests (21 tests) | ✅ All Passing |
| Docker Containerization | ✅ Complete |
| Architecture Diagrams | ✅ Complete |

---

## 📈 Dashboard Features

- KPI metrics with live filter updates
- Price distribution by room type (violin plots)
- Neighbourhood supply and pricing analysis
- Host market structure analysis
- Interactive listing price heatmap
- Market growth trend with COVID annotation
- Sidebar filters: room type, price range, neighbourhood, superhost

---

## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Data Processing:** pandas, numpy, duckdb
- **Statistics:** scipy, statsmodels
- **ML:** scikit-learn (Ridge, Random Forest, Gradient Boosting)
- **NLP:** VADER sentiment, TF-IDF RAG
- **Visualization:** plotly, matplotlib, seaborn
- **Dashboard:** Streamlit
- **Testing:** pytest (21 tests)
- **Containers:** Docker, docker-compose
- **Version Control:** Git + GitHub

---

## 📄 Report

Full analysis report: `report/Bangkok_Airbnb_Intelligence_Report.pdf`

---

## 🤖 AI Usage

AI tools (Claude Sonnet 4.6, GitHub Copilot) used as productivity multipliers. Full disclosure in Appendix A of the report.

---

## 👤 Author

**Primesh Marasinghe**  
BSc (Hons) Data Science — SLIIT  
[GitHub](https://github.com/primemarasinghe/airbnb-market-intelligence)