# Bangkok Airbnb Market Intelligence Report
### Expernetic Data Engineer Intern Assessment
**Prepared by:** Primesh Marasinghe  
**Date:** June 2026  
**Dataset:** Inside Airbnb — Bangkok, Thailand (September 2025 Scrape)

---

## 1. Executive Summary

The Bangkok short-term rental market represents one of Southeast Asia's most dynamic 
and commercially significant Airbnb ecosystems. This report presents a comprehensive 
analysis of 28,806 active listings across 50 neighbourhoods, derived from the Inside 
Airbnb public dataset scraped in September 2025.

**Key Findings:**

- **Market Scale:** Bangkok hosts 28,806 listings managed by 8,874 unique hosts, 
  with a median nightly price of ฿1,383 THB (~$38 USD).

- **Market Concentration:** A small cohort of commercial operators (10.6% of hosts) 
  controls 57% of all listings — a significant supply-side concentration with 
  implications for platform policy and pricing competition.

- **Price Drivers:** Room type and neighbourhood are the dominant price determinants. 
  Entire-home listings command a statistically significant 38% premium over private 
  rooms (฿1,491 vs ฿1,080 median, p<0.0001). Neighbourhood alone explains 10.5% 
  of price variance (η²=0.1055).

- **Quality Signal:** Superhost status correlates meaningfully with guest satisfaction 
  (4.86 vs 4.58 average rating, Cohen's d=0.54) but not with price premium — 
  suggesting hosts are not monetizing quality effectively.

- **Market Recovery:** Post-COVID recovery is complete and accelerating. Review volume 
  reached an all-time high of 148,869 in 2024, with 2025 on track to surpass it.

- **Seasonality:** Peak occupancy occurs July–September (43%), aligning with European 
  summer travel patterns. Weekend pricing shows no statistically significant premium 
  (p=0.526), confirming Bangkok's leisure-dominant, globally distributed tourist base.

**Recommendations for Market Participants:**
1. Hosts should pursue Superhost status as a quality signal — current data suggests 
   significant rating uplift without requiring price discounts.
2. Investors should prioritize Bang Rak and Vadhana for premium positioning.
3. Platform operators should monitor commercial host concentration as a regulatory risk.


## 2. Objectives & Scope

### 2.1 Project Objectives

This assessment was undertaken as part of the Expernetic Data Engineer Intern 
Technical Assignment. The primary objectives were:

1. Design and implement a production-quality data engineering pipeline for 
   ingesting, profiling, cleaning, and enriching publicly available Airbnb data.
2. Conduct rigorous exploratory data analysis to surface actionable market insights.
3. Apply formal statistical methods to validate or refute hypotheses about the 
   Bangkok Airbnb marketplace.
4. Build an interactive business intelligence dashboard for non-technical stakeholders.
5. Document all engineering decisions, assumptions, and limitations transparently.

### 2.2 City Selection

**Selected City: Bangkok, Thailand**

Bangkok was selected for the following reasons:

- **Dataset richness:** 28,806 listings provide sufficient statistical power for 
  hypothesis testing and segmentation analysis.
- **Market dynamism:** Bangkok is one of the world's top tourist destinations, 
  offering interesting pricing dynamics across diverse neighbourhood types.
- **Data recency:** The September 2025 scrape is among the most recent available, 
  ensuring findings reflect current market conditions.
- **Personal relevance:** As a Sri Lanka-based analyst, Southeast Asian market 
  dynamics are directly applicable to regional business contexts.

### 2.3 Prioritization Rationale

Given the one-week timeline, sections were prioritized as follows:

| Priority | Section | Rationale |
|----------|---------|-----------|
| 1 | Data Engineering (§03) | Core role competency, highest rubric weight |
| 2 | EDA (§04) | Foundation for all downstream analysis |
| 3 | Statistical Analysis (§05) | Differentiates analytical depth |
| 4 | Dashboard (§08) | Demonstrates creativity and initiative |
| 5 | Report & Documentation | Primary evaluation artifact |

Sections 06 (ML Modeling) and 07 (NLP/LLM) were deprioritized in favor of 
exceptional depth in the above sections, consistent with the assignment's stated 
design philosophy: *"quality outweighs quantity."*

### 2.4 Scope Boundaries

- Single city analysis (Bangkok) with full pipeline depth
- Calendar price analysis limited due to null price fields in source data 
  (documented in §3.4)
- No cloud deployment; architecture discussed conceptually in §5

## 3. Dataset Overview

### 3.1 Data Source

All data sourced exclusively from Inside Airbnb (insideairbnb.com), an independent, 
non-commercial project that scrapes publicly available Airbnb listing data. The 
Bangkok dataset reflects a scrape conducted in September 2025.

### 3.2 Files Used

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| listings.csv | 28,806 | 79 | Core listing attributes, host info, pricing, amenities |
| calendar.csv | 10,514,202 | 7 | Daily availability per listing (365 days forward) |
| reviews.csv | 583,333 | 6 | Guest review text and metadata |
| neighbourhoods.csv | 50 | 2 | Neighbourhood names and groupings |
| neighbourhoods.geojson | 50 | — | Geospatial polygon boundaries |

### 3.3 Entity Relationships
listings (id) ──────────< calendar (listing_id)

listings (id) ──────────< reviews (listing_id)

listings (host_id) >────── hosts (embedded in listings)

listings (neighbourhood_cleansed) >── neighbourhoods (neighbourhood)

**Primary Keys:** listings.id, reviews.id  
**Foreign Keys:** calendar.listing_id → listings.id, reviews.listing_id → listings.id

### 3.4 Data Limitations & Scraping Artifacts

| Issue | Impact | Handling |
|-------|--------|----------|
| calendar.price entirely null | Cannot compute true revenue | Proxy using listing price × availability_365 |
| neighbourhood_group_cleansed 100% null | No district-level grouping | Used neighbourhood_cleansed (50 groups) |
| license 100% null | Cannot assess regulatory compliance | Excluded from analysis |
| review scores ~35% missing | Ratings analysis on subset only | Documented, subset used |
| host_neighbourhood ~67% missing | Cannot map host locations | Excluded from analysis |
| Price outliers up to ฿1,000,000 | Skews mean calculations | 99th percentile filtering applied |

### 3.5 Assumptions

1. **Occupancy proxy:** Estimated as `1 - (availability_365 / 365)`. This assumes 
   unavailable days reflect bookings, not host blocking — a known limitation of 
   Inside Airbnb methodology.
2. **Revenue proxy:** `price × (365 - availability_365)`. Uses listed price, not 
   actual transaction price.
3. **Price validity:** Records with price = 0 or price < 0 flagged but retained 
   in dataset; excluded from price analysis.
4. **Coordinate validity:** Bangkok listings expected within latitude 12–15°N, 
   longitude 100–101°E. Records outside this range flagged.
5. **Review volume as demand proxy:** Higher review counts interpreted as higher 
   booking activity, consistent with Inside Airbnb methodology documentation.

### 3.6 Business Domain Context

| Entity | Business Meaning |
|--------|-----------------|
| Listing | A rentable property unit with defined pricing and availability |
| Host | Property owner or manager; may manage single or multiple listings |
| Review | Post-stay guest feedback; primary demand signal in the dataset |
| Calendar | Forward-looking availability schedule set by host |
| Neighbourhood | Administrative sub-district used for geographic segmentation |

## 4. Methodology

### 4.1 Overall Analytical Approach

This project followed a structured data engineering and analytics workflow:
Raw Data Ingestion → Profiling → Cleaning → Enrichment → Star Schema → EDA → Hypothesis Testing → Dashboard → Report

Each stage produced validated, documented outputs before the next stage began — 
consistent with production data engineering practice.

### 4.2 Tool Selection & Rationale

| Category | Tool Selected | Alternatives Considered | Rationale |
|----------|-------------|------------------------|-----------|
| Language | Python 3.11 | R, Scala | Ecosystem breadth, pandas/scipy integration |
| Data Processing | pandas | polars, DuckDB | Familiarity, sufficient for single-city scale |
| Statistical Testing | scipy.stats | statsmodels, R | Comprehensive non-parametric test support |
| Visualization | plotly, matplotlib/seaborn | Altair, Tableau | Interactive + static output flexibility |
| Dashboard | Streamlit | Dash, Gradio | Rapid deployment, Python-native |
| Database | CSV + star schema files | DuckDB, SQLite | Sufficient for assessment scope |
| Version Control | Git + GitHub | — | Required by assignment |

### 4.3 Statistical Methodology

All hypothesis tests followed this protocol:

1. **State null and alternative hypotheses explicitly**
2. **Check normality** using Shapiro-Wilk test on samples
3. **Select appropriate test** — Mann-Whitney U for non-normal distributions 
   (confirmed for all price variables), Kruskal-Wallis for multi-group comparisons
4. **Report effect sizes** alongside p-values — rank-biserial correlation and 
   Cohen's d for pairwise tests, eta-squared for ANOVA-equivalent tests
5. **Interpret in business terms** — statistical significance distinguished from 
   practical significance throughout

### 4.4 Data Quality Framework

A systematic data quality assessment was performed across five dimensions:

| Dimension | Method |
|-----------|--------|
| Completeness | Null rate per column, flagged fields >50% missing |
| Validity | Domain rule checks (price ≥ 0, valid coordinates) |
| Uniqueness | Duplicate detection on listing ID |
| Consistency | Standardization of boolean, categorical, and currency fields |
| Timeliness | Scrape date documented; recency assessed per city |

### 4.5 Outlier Handling

Price outliers were handled conservatively:
- Records retained in cleaned dataset with flag columns
- 99th percentile filtering applied for visualization and hypothesis testing
- Extreme values (e.g., ฿1,000,000 listings) noted as likely data entry errors 
  or luxury property placeholders, documented as a dataset limitation

  ## 5. Engineering Approach

### 5.1 Pipeline Architecture

The pipeline follows a medallion-style layered architecture:

[Source]          [Bronze]           [Silver]            [Gold]

Inside Airbnb → Raw CSV files → Cleaned CSVs → Enriched master table

(ingest.py)    (data/raw/)     (clean.py)      (enrich.py)

→ Star schema tables

Each layer is produced by a dedicated, independently runnable script with 
logging, error handling, and retry logic.

### 5.2 Pipeline Components

**ingest.py — Data Ingestion**
- Configurable city-level download via BASE_URL parameter
- Retry logic (3 attempts) with exponential backoff
- Automatic .gz extraction
- JSON metadata file recording ingestion timestamp, source URL, and file status
- Supports any Inside Airbnb city with single config change

**profile.py — Data Profiling**
- Automated profiling of all ingested files
- Reports: row counts, column cardinality, null rates, data type distributions,
  min/max/mean for numerical fields, sample values for categorical fields
- Output: structured JSON report for documentation and audit trail

**clean.py — Data Cleaning**
- Price standardization: currency symbol removal, thousands separator handling,
  cast to float64
- Date parsing across all temporal fields
- Boolean normalization (t/f → True/False)
- Percentage field conversion (host_response_rate, host_acceptance_rate)
- Derived fields: host_tenure_years, price_per_bedroom
- Validation flags: flag_negative_price, flag_zero_price, flag_invalid_coords
- Duplicate detection on listing ID

**enrich.py — Data Enrichment**
- Neighbourhood-level aggregates joined to listings:
  median price, listing count, average rating
- Occupancy rate computation from availability_365
- Revenue estimation proxy (documented assumption)
- Host segmentation: Single (1 listing), Small Multi (2–5), Commercial (6+)
- Review frequency calculation (reviews per month of host tenure)
- Star schema construction: fact_listings, dim_host, dim_location,
  dim_property, dim_review_scores

### 5.3 Star Schema Design

                    ┌─────────────────┐
                    │   dim_host      │
                    │  host_id (PK)   │
                    │  host_name      │
                    │  host_since     │
                    │  is_superhost   │
                    │  host_type      │
                    └────────┬────────┘
                             │
┌──────────────┐    ┌────────▼────────┐    ┌─────────────────────┐

│ dim_location │    │  fact_listings  │    │   dim_property      │

│ location_id  ├────│  listing_id(PK) ├────│   listing_id (PK)   │

│ neighbourhood│    │  host_id (FK)   │    │   room_type         │

│ median_price │    │  location_id(FK)│    │   property_type     │

│ listing_count│    │  price          │    │   accommodates      │

│ avg_rating   │    │  occupancy_rate │    │   bedrooms/beds     │

└──────────────┘    │  est_revenue    │    └─────────────────────┘

                    │  booked_days    │

                    │  review_freq    │    ┌─────────────────────┐

                    └────────┬────────┘    │  dim_review_scores  │

                             │             │  listing_id (PK)    │

                             └─────────────│  rating             │

                                           │  cleanliness        │

                                           │  location           │

                                           │  communication      │

                                           └─────────────────────┘

### 5.4 Engineering Decision Log

| Decision | Options Considered | Choice | Trade-off Accepted |
|----------|-------------------|--------|--------------------|
| Storage format | SQLite, DuckDB, CSV | CSV + star schema files | Portability over query performance |
| Pipeline orchestration | Airflow, Prefect, scripts | Python scripts | Simplicity over scheduling capability |
| Outlier handling | Remove, cap, flag | Flag + filter at analysis layer | Preserve raw data integrity |
| Occupancy calculation | Calendar-based, availability-based | availability_365 proxy | Calendar prices unavailable for Bangkok |
| Dashboard framework | Dash, Streamlit, Gradio | Streamlit | Fastest path to deployable product |

### 5.5 Incremental Processing Design

For production deployment, incremental processing would be implemented as follows:

1. **Metadata tracking:** Each ingestion records timestamp and file hash in 
   `ingest_metadata.json`
2. **Change detection:** Compare file hash of new scrape against stored hash; 
   skip if unchanged
3. **Merge strategy:** New listings upserted by listing_id; deleted listings 
   flagged with `is_active=False` rather than hard-deleted (SCD Type 2)
4. **Calendar data:** Append-only with date partitioning; past dates never 
   reprocessed
5. **Review data:** Append new reviews by review_id; existing reviews immutable

### 5.6 Production Readiness Considerations

| Concern | Current State | Production Recommendation |
|---------|--------------|--------------------------|
| Scalability | Single-city, local | Parameterized multi-city, cloud storage |
| Monitoring | File logging | Structured logging + alerting (PagerDuty) |
| Data quality | Manual review | Great Expectations automated checks |
| Scheduling | Manual execution | Airflow DAG triggered post-scrape |
| Infrastructure | Local filesystem | AWS S3 + Glue + Athena or GCP BigQuery |

## 6. EDA Findings

### 6.1 Price Distribution

The Bangkok Airbnb market exhibits a strongly right-skewed price distribution, 
with a median nightly price of ฿1,383 THB and a mean of ฿2,768 THB — a large 
gap driven by extreme luxury outliers (max: ฿1,000,000).

**Key statistics:**
- Median: ฿1,383 THB (~$38 USD)
- Mean: ฿2,768 THB (~$76 USD)
- 75th percentile: ฿2,415 THB
- Listings above ฿5,000: ~8% of market

**Business interpretation:** The median price positions Bangkok as an 
affordable short-term rental market by global standards, attracting budget 
and mid-range travelers. The long right tail reflects a small luxury segment 
serving premium tourists and corporate travelers. Hosts pricing above ฿5,000 
operate in a fundamentally different competitive environment requiring distinct 
marketing and positioning strategies.

### 6.2 Room Type Analysis

| Room Type | Count | Share | Median Price | Avg Occupancy |
|-----------|-------|-------|-------------|---------------|
| Entire Home/Apt | 18,845 | 65.4% | ฿1,491 | 31.1% |
| Private Room | 9,224 | 32.0% | ฿1,080 | 32.7% |
| Hotel Room | 387 | 1.3% | ฿1,709 | 37.5% |
| Shared Room | 350 | 1.2% | ฿360 | 11.6% |

**Business interpretation:** Entire homes dominate supply and command a 38% 
price premium, yet private rooms achieve slightly higher occupancy — suggesting 
price-sensitive demand absorbs private room inventory more efficiently. Hotel 
rooms achieve the highest occupancy despite premium pricing, reflecting brand 
trust and booking platform visibility advantages.

### 6.3 Neighbourhood Analysis

**Top 5 neighbourhoods by listing count:**
1. Vadhana — 4,305 listings, median ฿1,828
2. Khlong Toei — 3,620 listings, median ฿1,622
3. Huai Khwang — 3,460 listings, median ฿1,400
4. Ratchathewi — 1,563 listings, median ฿1,588
5. Sathon — 1,326 listings, median ฿1,165

**Business interpretation:** Vadhana and Khlong Toei dominate supply, 
reflecting Bangkok's concentration of modern condominiums in the Sukhumvit 
corridor — a zone favored by both tourists and expatriates. Bang Rak commands 
the highest median price (฿1,890) despite lower supply, suggesting premium 
demand for its riverside and business district location. Investors seeking 
yield should consider Bang Rak for pricing power and Vadhana for liquidity.

### 6.4 Host & Supply-Side Analysis

The Bangkok market exhibits significant supply concentration:

- **8,874** unique hosts manage **28,806** listings
- **62.7%** of hosts operate a single listing (casual hosts)
- **10.6%** of hosts (944) operate 6+ listings (commercial operators)
- Commercial operators control **57%** of all listings
- Top single host manages **243 listings**

**Business interpretation:** Bangkok's Airbnb market is not a peer-to-peer 
sharing economy — it is a professionally managed short-term rental market 
dominated by commercial operators. This has significant implications: pricing 
is more sophisticated, availability is more actively managed, and regulatory 
risk is higher. Platform operators should monitor this concentration as 
regulators in other markets (Barcelona, Amsterdam) have targeted commercial 
operators specifically.

### 6.5 Occupancy & Revenue Analysis

- Mean occupancy rate: **31.5%** (availability_365 proxy)
- Median occupancy rate: **20.6%**
- Median estimated annual revenue: **฿61,848** (~$1,700 USD)
- Mean estimated annual revenue: **฿203,274** (~$5,600 USD)

**Business interpretation:** The wide gap between mean and median revenue 
confirms a highly skewed distribution — a small number of high-performing 
listings generate disproportionate revenue. The median host earns approximately 
฿5,154/month from their listing — a meaningful supplementary income in the 
Thai context but insufficient as a primary income source for most hosts.

### 6.6 Seasonal Trends

| Period | Occupancy Rate |
|--------|---------------|
| Jan | 27.7% |
| Feb | 24.4% |
| Mar | 23.4% |
| Apr | 28.3% |
| May | 27.6% |
| Jun | 30.5% |
| Jul | 41.8% |
| Aug | 41.6% |
| Sep | 43.2% |
| Oct | 33.4% |
| Nov | 27.7% |
| Dec | 27.6% |

**Business interpretation:** A pronounced July–September peak (41–43% 
occupancy) aligns with European summer holidays — Bangkok's primary tourist 
source market. The February trough (24.4%) represents the lowest demand 
period despite being a traditional high season in Thai tourism, possibly 
reflecting post-Chinese New Year softness. Hosts should implement dynamic 
pricing strategies that capture the July–September premium while stimulating 
demand in Q1 trough periods.

### 6.7 Review Score Analysis

- Mean rating: **4.69 / 5.00**
- Listings rated above 4.5: **81.4%**

**Business interpretation:** The extreme concentration of ratings above 4.5 
is a classic rating inflation pattern observed across Airbnb markets globally. 
This compression makes it difficult for guests to differentiate quality using 
scores alone, and for hosts to signal genuine quality improvements. Sub-score 
dimensions (cleanliness, location, communication) provide more discriminating 
signals for discerning guests.

### 6.8 Market Recovery Post-COVID

| Year | Reviews |
|------|---------|
| 2019 | 59,010 |
| 2020 | 18,014 |
| 2021 | 5,171 |
| 2022 | 40,567 |
| 2023 | 97,184 |
| 2024 | 148,869 |
| 2025 | 122,916* |

*2025 partial year (through September scrape)

**Business interpretation:** Bangkok's Airbnb market has not merely recovered 
from COVID — it has surpassed pre-pandemic peaks by 152%. This exceptional 
growth reflects both pent-up travel demand and Thailand's aggressive tourism 
promotion strategy. The trajectory strongly supports continued investment in 
Bangkok short-term rental assets.

## 7. Statistical Findings

### 7.1 Methodology Note

All price variables were confirmed non-normally distributed via Shapiro-Wilk 
test (p<0.0001 for all groups). Consequently, non-parametric tests were applied 
throughout: Mann-Whitney U for pairwise comparisons and Kruskal-Wallis for 
multi-group comparisons. Effect sizes are reported alongside p-values in all 
cases, as statistical significance alone is insufficient for practical inference 
at large sample sizes.

### 7.2 Hypothesis Testing Results

---

**H1: Entire-home listings command significantly higher prices than private rooms**

- **Test:** Mann-Whitney U (one-tailed)
- **H₀:** Median price of entire homes ≤ median price of private rooms
- **H₁:** Median price of entire homes > median price of private rooms
- **Entire home median:** ฿1,491 THB (n=16,498)
- **Private room median:** ฿1,080 THB (n=6,263)
- **U statistic:** 65,397,289
- **P-value:** <0.0001
- **Effect size (rank-biserial r):** -0.2916 (moderate)
- **Decision:** REJECT H₀

**Business interpretation:** Entire-home listings command a statistically 
significant and practically meaningful 38% price premium over private rooms. 
This premium reflects guest preference for privacy and exclusive access. 
Hosts considering property type positioning should factor this premium against 
the higher capital requirement of entire-home listings.

---

**H2: Superhost listings achieve higher review scores than non-superhost listings**

- **Test:** Mann-Whitney U (one-tailed)
- **H₀:** Superhost median rating ≤ non-superhost median rating
- **H₁:** Superhost median rating > non-superhost median rating
- **Superhost mean rating:** 4.858 (n=6,929)
- **Non-superhost mean rating:** 4.575 (n=10,540)
- **P-value:** <0.0001
- **Effect size (rank-biserial r):** -0.3261
- **Cohen's d:** 0.5364 (medium-large)
- **Decision:** REJECT H₀

**Business interpretation:** Superhost status is a genuine quality signal, 
not merely a marketing badge. A Cohen's d of 0.54 represents a meaningful 
real-world difference in guest experience. Notably, superhosts do not charge 
significantly higher prices (฿1,390 vs ฿1,371 median) — suggesting hosts 
are undermonetizing their quality advantage. Revenue optimization strategies 
for superhosts should include gradual price testing.

---

**H3: Listings with more than 10 reviews have significantly different prices**

- **Test:** Mann-Whitney U (two-tailed)
- **H₀:** No price difference between high-review and low-review listings
- **>10 reviews median price:** ฿1,345 THB (n=8,017)
- **≤10 reviews median price:** ฿1,386 THB (n=15,022)
- **P-value:** 0.000005
- **Effect size (rank-biserial r):** 0.0365 (negligible)
- **Decision:** REJECT H₀ — but effect is statistically significant, 
  practically negligible

**Business interpretation:** While the test rejects the null hypothesis, 
the effect size of 0.037 is negligible — the ฿41 difference has no practical 
significance for pricing decisions. This finding illustrates the critical 
importance of reporting effect sizes alongside p-values: with n=23,039, 
even trivial differences achieve statistical significance. Interestingly, 
listings with more reviews are slightly cheaper, suggesting budget listings 
attract higher booking volumes.

---

**H4: Neighbourhood average prices differ significantly across Bangkok**

- **Test:** Kruskal-Wallis H (non-parametric ANOVA equivalent)
- **H₀:** Median prices are equal across all neighbourhoods
- **Groups tested:** 10 highest-supply neighbourhoods
- **H statistic:** 1,726.68
- **P-value:** <0.0001
- **Eta-squared (η²):** 0.1055 (moderate)
- **Decision:** REJECT H₀

**Neighbourhood median prices (THB):**

| Neighbourhood | Median Price |
|--------------|-------------|
| Bang Rak | ฿1,890 |
| Vadhana | ฿1,828 |
| Khlong Toei | ฿1,622 |
| Ratchathewi | ฿1,588 |
| Huai Khwang | ฿1,400 |
| Phra Khanong | ฿1,184 |
| Sathon | ฿1,165 |
| Chatu Chak | ฿1,130 |
| Phra Nakhon | ฿1,103 |
| Suanluang | ฿1,045 |

**Business interpretation:** Neighbourhood explains 10.5% of price variance 
— a meaningful location premium effect. Bang Rak commands an 81% premium 
over Suanluang, reflecting its riverside location and proximity to the CBD. 
For investors and hosts, neighbourhood selection is the single most impactful 
positioning decision after room type.

---

**H5: Weekend pricing differs significantly from weekday pricing**

- **Test:** Mann-Whitney U (two-tailed)
- **H₀:** No difference in weekend vs weekday prices
- **Weekend median:** ฿1,383 THB
- **Weekday median:** ฿1,380 THB
- **P-value:** 0.5259
- **Effect size (rank-biserial r):** 0.0023 (negligible)
- **Cohen's d:** -0.012 (negligible)
- **Decision:** FAIL TO REJECT H₀

**Business interpretation:** Bangkok hosts do not implement meaningful 
weekend pricing premiums — a significant missed revenue opportunity compared 
to markets like London or New York where weekend premiums of 15–25% are 
common. This likely reflects Bangkok's tourist-dominant demand base, where 
visitors stay across the full week rather than weekend-only. Dynamic pricing 
tools could help hosts experiment with weekend premiums to capture additional 
revenue without meaningfully impacting occupancy.

### 7.3 Summary Table

| Hypothesis | Test | P-value | Effect Size | Practical Significance | Decision |
|-----------|------|---------|-------------|----------------------|----------|
| H1: Entire home > Private room price | Mann-Whitney U | <0.0001 | r=-0.29 (moderate) | Yes — 38% premium | REJECT H₀ |
| H2: Superhost > Non-superhost rating | Mann-Whitney U | <0.0001 | d=0.54 (medium) | Yes — meaningful quality gap | REJECT H₀ |
| H3: >10 reviews ≠ price | Mann-Whitney U | 0.000005 | r=0.037 (negligible) | No — ฿41 difference | REJECT H₀* |
| H4: Neighbourhood price differences | Kruskal-Wallis | <0.0001 | η²=0.11 (moderate) | Yes — 81% range | REJECT H₀ |
| H5: Weekend ≠ Weekday price | Mann-Whitney U | 0.5259 | d=-0.012 (negligible) | No | FAIL TO REJECT H₀ |

*Statistically significant but practically negligible effect size.

## 8. Data Science Experiments

This section was deprioritized in favor of exceptional depth in data engineering 
and statistical analysis, consistent with the assignment's design philosophy. 
The following outlines the approach that would be taken with additional time.

### 8.1 Price Prediction — Planned Approach

**Problem framing:** Predict nightly listing price given property attributes, 
host characteristics, and location features. Target variable: log-transformed 
price (to address right skew).

**Feature engineering plan:**
- Amenity flags extracted from JSON amenities field (WiFi, pool, parking, etc.)
- Encoded categorical variables: room_type, neighbourhood, property_type
- Interaction terms: room_type × neighbourhood, accommodates × bedrooms
- Host features: tenure, superhost status, response rate
- Location features: neighbourhood median price, listing density

**Model comparison plan:**

| Model | Rationale |
|-------|-----------|
| Ridge Regression | Baseline linear model, interpretable coefficients |
| Random Forest | Captures non-linear relationships, feature importance |
| XGBoost | State-of-art gradient boosting, handles mixed types |

**Validation strategy:** 5-fold cross-validation, metrics: MAE, RMSE, MAPE.
SHAP values for feature importance and explainability.

**Expected finding:** Location (neighbourhood) and room type expected to be 
dominant features, consistent with correlation analysis findings in §6.

---

## 9. AI/ML Experiments

### 9.1 LLM Usage in This Project

Claude (Anthropic) was used throughout this project as an AI coding assistant. 
Full disclosure is provided in Appendix A.

### 9.2 Planned NLP Analysis

With additional time, the following NLP analyses would be applied to the 
583,333 guest reviews:

**Sentiment analysis:** Apply VADER or a fine-tuned transformer model to 
correlate review sentiment with numerical scores. Hypothesis: sentiment 
divergence from numerical score identifies inflated ratings.

**Topic modeling:** BERTopic on review corpus to surface recurring themes 
(cleanliness complaints, location praise, host responsiveness, noise issues).

**Named entity extraction:** spaCy NER to extract mentioned landmarks, 
amenities, and complaint categories — enabling automated listing improvement 
recommendations.

---

## 10. Visualizations

All visualizations are available in the interactive dashboard 
(dashboard/app.py) and as static figures in notebooks/figures/.

| Figure | Description |
|--------|-------------|
| 01_price_distribution.png | Nightly price histogram — full range and zoomed |
| 02_room_type_analysis.png | Median price and listing count by room type |
| 03_neighbourhood_analysis.png | Top 20 neighbourhoods by price and supply |
| 04_host_analysis.png | Host type distribution and portfolio size distribution |
| 05_availability_occupancy.png | Availability and occupancy rate distributions |
| 06_seasonal_trends.png | Monthly occupancy and weekend vs weekday comparison |
| 07_review_trends.png | Review volume by year and monthly seasonality |
| 08_ratings_superhost.png | Rating distribution and superhost comparison |
| 09_correlation_matrix.png | Correlation heatmap of numerical features |
| H1_price_roomtype.png | Hypothesis H1 boxplot |
| H2_superhost_ratings.png | Hypothesis H2 boxplot |

---

## 11. Business Recommendations

Based on the analysis, the following actionable recommendations are made 
for key market participants:

### For Hosts

**1. Pursue Superhost status aggressively**
Superhost listings achieve ratings 0.28 points higher (Cohen's d=0.54) 
with no meaningful price premium currently. This represents an undermonetized 
quality signal. Superhosts should gradually test 5–10% price increases, 
as the quality gap justifies premium pricing.

**2. Implement dynamic pricing for July–September peak**
Occupancy jumps from ~25% in Q1 to 43% in September. Hosts not using 
dynamic pricing tools (Wheelhouse, PriceLabs) are leaving significant 
revenue on the table during peak season.

**3. Test weekend pricing premiums**
H5 confirmed no current weekend premium exists in Bangkok. Early adopters 
implementing 10–15% weekend surcharges face minimal competitive risk and 
meaningful revenue upside.

**4. Prioritize Bang Rak and Vadhana for investment**
Bang Rak commands the highest median price (฿1,890) with strong demand. 
Vadhana offers the deepest market (4,305 listings) with high liquidity 
for entry and exit.

### For Platform Operators

**5. Monitor commercial host concentration**
57% of listings controlled by commercial operators represents a regulatory 
risk. Bangkok's market structure mirrors pre-regulation Amsterdam and 
Barcelona. Proactive engagement with Thai regulators is advisable.

**6. Address rating inflation**
81.4% of listings rated above 4.5 compresses the signal value of ratings. 
Sub-score dimensions (cleanliness, location, communication) should be 
promoted as primary quality indicators.

### For Investors

**7. Bangkok market fundamentals are strong**
2024 review volume exceeded pre-COVID peaks by 152%. With Thailand's 
continued tourism promotion and improving infrastructure, the Bangkok 
short-term rental market presents a favorable investment environment.

**8. Focus on mid-market entire homes**
The ฿1,000–2,500 price range captures the highest demand concentration. 
Luxury listings (>฿5,000) face thinner demand and higher vacancy risk.

## 12. Cross-City Comparisons

Single-city analysis was conducted for this assessment. The following 
outlines how cross-city comparison would be approached with additional time.

### 12.1 Planned Comparison Markets

| City | Rationale |
|------|-----------|
| Singapore | Regional premium market benchmark |
| Kuala Lumpur | Similar SEA tourist profile |
| Ho Chi Minh City | Emerging competitor market |

### 12.2 Harmonization Strategy

Cross-city analysis would require:
1. Standardized currency conversion (all prices to USD at scrape-date rate)
2. Consistent neighbourhood taxonomy (admin level 2 for all cities)
3. Unified room type categories (Inside Airbnb uses consistent taxonomy)
4. Scrape date alignment (within 90-day window for comparability)
5. Population normalization for listing density comparisons

### 12.3 Expected Insights

- Bangkok expected to show lower price points than Singapore but higher 
  than Ho Chi Minh City
- Commercial host concentration likely highest in Bangkok vs regional peers
- Seasonal patterns expected to diverge significantly across cities

---

## 13. Limitations & Caveats

### 13.1 Data Limitations

| Limitation | Impact | Severity |
|-----------|--------|----------|
| Calendar prices entirely null | Revenue estimates are proxies only | High |
| Occupancy from availability_365 | Conflates host blocking with bookings | Medium |
| Single scrape date | No longitudinal price tracking | Medium |
| Review scores 35% missing | Ratings analysis on subset | Medium |
| No transaction data | Cannot verify actual bookings | High |
| Scraping artifacts | Some listings may be inactive | Low |

### 13.2 Methodological Limitations

**Occupancy proxy:** The `availability_365` field records days marked 
unavailable by hosts, which may reflect bookings OR deliberate blocking 
(e.g., host traveling, property maintenance). Inside Airbnb acknowledges 
this limitation in their methodology documentation. True occupancy is 
likely lower than estimated.

**Revenue estimation:** Using listed price × estimated booked days 
overstates revenue for listings that offer discounts for longer stays 
and understates for listings with dynamic pricing premiums.

**Causality:** All findings are correlational. Superhost status correlating 
with higher ratings does not establish that achieving superhost status causes 
rating improvement — selection effects are present.

**Temporal validity:** The September 2025 scrape reflects a single point 
in time. Market conditions, pricing strategies, and competitive dynamics 
evolve continuously.

### 13.3 Statistical Limitations

- Large sample sizes (n>8,000 for most tests) make even trivial differences 
  statistically significant — effect sizes must be interpreted carefully
- Multiple hypothesis testing without Bonferroni correction applied — 
  familywise error rate is elevated across 5 tests
- Non-independence of listings from same host violates independence 
  assumptions of standard tests

---

## 14. Future Improvements

### 14.1 With More Time

| Improvement | Value |
|-------------|-------|
| ML price prediction with SHAP explainability | Quantify feature importance |
| NLP sentiment analysis on 583K reviews | Surface quality signals beyond scores |
| Multi-city comparative analysis | Regional market benchmarking |
| Geospatial clustering with GeoPandas/Folium | Neighbourhood boundary visualization |
| dbt models for documented lineage | Production-grade transformation layer |
| Great Expectations data quality checks | Automated quality gates |

### 14.2 With Better Data

| Data Gap | What It Would Enable |
|----------|---------------------|
| Actual transaction prices | True revenue modeling |
| Booking timestamps | Real occupancy calculation |
| Guest demographics | Demand segmentation |
| Host cost data | True profitability analysis |
| Historical scrapes (12+ months) | Longitudinal price trend analysis |

### 14.3 With Production Infrastructure

- **Orchestration:** Apache Airflow DAG triggered weekly post-scrape
- **Storage:** AWS S3 data lake with Glue catalog
- **Processing:** Spark for multi-city parallel processing
- **Serving:** BigQuery + Looker Studio for stakeholder dashboards
- **Monitoring:** Great Expectations + Slack alerting for data quality failures
- **CI/CD:** GitHub Actions for automated pipeline testing on push

---

## 15. Reflection

### 15.1 Prioritization Decisions

The one-week timeline required deliberate prioritization. The core 
data engineering pipeline (ingestion, profiling, cleaning, enrichment, 
star schema) was completed first as the foundation for all downstream 
work. EDA and hypothesis testing followed as the primary analytical 
deliverables. The Streamlit dashboard was built as the open innovation 
component, demonstrating end-to-end product thinking.

ML modeling (Section 06) and NLP experiments (Section 07) were 
consciously deprioritized. Given the rubric weights — Problem Solving 
(30), Data Engineering Quality (25), Code Quality (20) — depth in 
engineering and statistical analysis offered higher expected value than 
superficial ML experiments.

### 15.2 Key Trade-offs Accepted

| Trade-off | Decision | Rationale |
|-----------|----------|-----------|
| Depth vs breadth | Single city, deep analysis | Assignment explicitly rewards depth |
| ML vs statistics | Formal hypothesis testing | More rigorous, higher rubric weight |
| Cloud vs local | Local pipeline, cloud design | Reproducibility without cloud costs |
| Speed vs quality | Slower, documented approach | Report quality is primary artifact |

### 15.3 Key Lessons Learned

1. **Data quality issues surface early or not at all** — the null calendar 
   prices were discovered during profiling, allowing time to design a 
   principled workaround rather than discovering it during analysis.

2. **Effect sizes matter as much as p-values** — H3 demonstrated that 
   statistical significance without practical significance is misleading, 
   reinforcing the importance of rigorous statistical reporting.

3. **Commercial concentration is a Bangkok-specific story** — the 57% 
   commercial operator finding was not anticipated and emerged from the 
   data, representing genuine discovery rather than hypothesis confirmation.

4. **Documentation is part of the engineering** — maintaining decision 
   logs, assumption documentation, and metadata throughout the pipeline 
   made the final report significantly easier to write and more credible.

---

## Appendix A — AI Usage Disclosure

### A.1 AI Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| Claude (Anthropic) | Claude Sonnet 4.6 | Primary coding assistant, report structuring |
| GitHub Copilot | — | Inline code completion |

### A.2 AI-Assisted Sections

| Section | AI Assistance Level | Description |
|---------|--------------------|-|
| Pipeline code (ingest, clean, enrich) | High | Generated with prompting, reviewed and modified |
| EDA notebook cells | High | Generated with prompting, all outputs verified |
| Hypothesis testing code | Medium | Generated, statistical choices independently verified |
| Dashboard CSS/layout | Medium | Generated, significantly modified for aesthetics |
| Report writing | Medium | Structure suggested, content written and verified |
| Business interpretations | Low | All business interpretations independently authored |
| Statistical conclusions | Low | All conclusions independently verified against outputs |

### A.3 Key Prompts Used

All interactions conducted with Claude Sonnet 4.6 via claude.ai. 
Representative prompts:

- *"Build a repeatable ingestion pipeline with retry logic and metadata 
  tracking for Inside Airbnb Bangkok data"*
- *"Clean the listings CSV — standardize price, parse dates, flag invalid 
  records, derive host tenure"*
- *"Run Mann-Whitney U test for H1 with effect size and business interpretation"*
- *"Build a dark-themed Streamlit dashboard with plotly charts for Bangkok 
  Airbnb data"*

### A.4 Output Validation

All AI-generated code was:
1. Executed and outputs verified against expected ranges
2. Reviewed for logical correctness before proceeding
3. Modified where outputs were incorrect (calendar price null issue 
   required independent diagnosis and resolution)
4. Statistical results cross-checked against manual calculations

### A.5 Critical Assessment

AI assistance was most valuable for boilerplate pipeline code and 
visualization scaffolding. It was least reliable for domain-specific 
business interpretations and statistical methodology choices — both 
areas where independent judgment was applied. The calendar price null 
issue was diagnosed independently after AI-generated code produced NaN 
outputs, demonstrating the necessity of critical evaluation.

AI tools were used as a productivity multiplier, not a replacement for 
analytical judgment. All findings, interpretations, and recommendations 
represent the author's independent analysis.