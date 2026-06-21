"""
Bangkok Airbnb AI Analyst — Cloud Version
Standalone deployment with hardcoded market data (no CSV files required)
"""
import streamlit as st
import re
from collections import Counter

st.set_page_config(
    page_title="Bangkok Airbnb AI Analyst",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}

.chat-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.8rem 0;
}

.chat-user-bubble {
    background: #1e3a5f;
    border-radius: 18px 18px 4px 18px;
    padding: 0.8rem 1.2rem;
    max-width: 70%;
    color: #e0e0e0;
    font-size: 0.95rem;
    line-height: 1.5;
}

.chat-assistant {
    display: flex;
    justify-content: flex-start;
    margin: 0.8rem 0;
    gap: 0.8rem;
    align-items: flex-start;
}

.chat-avatar {
    background: #00d4ff;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    margin-top: 4px;
}

.chat-assistant-bubble {
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 4px 18px 18px 18px;
    padding: 1rem 1.2rem;
    max-width: 80%;
    color: #e0e0e0;
    font-size: 0.92rem;
    line-height: 1.7;
}

.chat-assistant-bubble b { color: #00d4ff; }

[data-testid="stSidebar"] {
    background: #1a1f2e;
    border-right: 1px solid #2a2f3e;
}

div[data-testid="stTextInput"] input {
    background: #1a1f2e !important;
    border: 1px solid #2a2f3e !important;
    border-radius: 25px !important;
    color: #e0e0e0 !important;
    padding: 0.7rem 1.2rem !important;
}

div[data-testid="stButton"] button {
    border-radius: 25px !important;
    background: #00d4ff !important;
    color: #0e1117 !important;
    font-weight: 600 !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# Hardcoded market data from actual analysis
MARKET_DATA = {
    "total_listings": 28806,
    "unique_hosts": 8874,
    "neighbourhoods": 50,
    "total_reviews": 583333,
    "median_price": 1359,
    "mean_price": 2768,
    "avg_occupancy": 0.3147,
    "median_occupancy": 0.2055,
    "superhost_count": 7975,
    "commercial_pct": 57.0,
    "median_annual_revenue": 61848,
    "mean_annual_revenue": 203274,
    "superhost_revenue": 114431,
    "non_superhost_revenue": 25968,
    "superhost_rating": 4.858,
    "non_superhost_rating": 4.575,
    "mean_rating": 4.690,
    "pct_above_4_5": 81.4,
    "top_neighbourhoods": {
        "Vadhana": {"listings": 4305, "median_price": 1828},
        "Khlong Toei": {"listings": 3620, "median_price": 1622},
        "Huai Khwang": {"listings": 3460, "median_price": 1400},
        "Bang Rak": {"listings": 1141, "median_price": 1890},
        "Parthum Wan": {"listings": 550, "median_price": 2225},
    },
    "room_types": {
        "Entire Home/Apt": {"count": 18845, "median_price": 1491, "occupancy": 0.311},
        "Private Room": {"count": 9224, "median_price": 1080, "occupancy": 0.327},
        "Hotel Room": {"count": 387, "median_price": 1709, "occupancy": 0.375},
        "Shared Room": {"count": 350, "median_price": 360, "occupancy": 0.116},
    },
    "monthly_occupancy": {
        "Jan": 27.7, "Feb": 24.4, "Mar": 23.4, "Apr": 28.3,
        "May": 27.6, "Jun": 30.5, "Jul": 41.8, "Aug": 41.6,
        "Sep": 43.2, "Oct": 33.4, "Nov": 27.7, "Dec": 27.6
    },
    "yearly_reviews": {
        2019: 59010, 2020: 18014, 2021: 5171,
        2022: 40567, 2023: 97184, 2024: 148869
    },
    "amenity_premiums": {
        "TV": 68.6, "Hot Tub": 49.8, "Kitchen": 36.9,
        "Breakfast": 27.4, "Pets Allowed": 22.7, "Pool": 19.6,
        "WiFi": 14.1, "Gym": 9.4, "Parking": 8.9
    },
    "hypothesis_results": {
        "H1": {"result": "REJECT H0", "pvalue": "<0.0001", "effect": "r=0.29 moderate", "finding": "38% price premium for entire homes"},
        "H2": {"result": "REJECT H0", "pvalue": "<0.0001", "effect": "d=0.54 medium", "finding": "Superhosts rate 0.28 points higher"},
        "H3": {"result": "REJECT H0*", "pvalue": "0.000005", "effect": "r=0.037 negligible", "finding": "Statistically significant but practically meaningless"},
        "H4": {"result": "REJECT H0", "pvalue": "<0.0001", "effect": "η²=0.11 moderate", "finding": "Neighbourhood explains 10.5% of price variance"},
        "H5": {"result": "FAIL TO REJECT", "pvalue": "0.526", "effect": "d=0.012 negligible", "finding": "No weekend premium in Bangkok"},
    },
    "ml_results": {
        "Ridge": {"MAE": 655, "R2": 0.449, "MAPE": 42.1},
        "Random Forest": {"MAE": 501, "R2": 0.652, "MAPE": 29.2},
        "Gradient Boosting": {"MAE": 504, "R2": 0.662, "MAPE": 29.1},
    },
    "top_features": [
        ("bedrooms", 43.2), ("neighbourhood_median_price", 16.9),
        ("accommodates", 12.2), ("host_tenure_years", 4.3),
        ("host_listing_count_actual", 4.3)
    ],
    "nlp_results": {
        "positive_pct": 72.9, "neutral_pct": 22.7, "negative_pct": 4.4,
        "top_landmark": "BTS (2,513 mentions)",
        "top_amenity": "Pool (1,474 mentions)",
        "top_complaint": "Small rooms (679 mentions)",
        "informative_pct": 24.1, "superficial_pct": 25.6
    }
}

def answer_question(question):
    q = question.lower()
    md = MARKET_DATA

    if any(w in q for w in ["price", "cost", "expensive", "cheap", "rate"]):
        top5_nb = "".join([
            f"• {nb}: <b>฿{data['median_price']:,}</b> median ({data['listings']:,} listings)<br>"
            for nb, data in md["top_neighbourhoods"].items()
        ])
        return f"""<b>Bangkok Airbnb Pricing Analysis</b><br><br>
<b>Market Overview:</b><br>
- Median nightly price: <b>฿{md['median_price']:,} THB</b> (~$38 USD)<br>
- Mean price: ฿{md['mean_price']:,} THB (skewed by luxury outliers)<br>
- Price range: ฿100 – ฿10,000+ (luxury segment)<br><br>
<b>By Room Type:</b><br>
- Entire Home/Apt: <b>฿{md['room_types']['Entire Home/Apt']['median_price']:,}</b> median<br>
- Hotel Room: <b>฿{md['room_types']['Hotel Room']['median_price']:,}</b> median<br>
- Private Room: <b>฿{md['room_types']['Private Room']['median_price']:,}</b> median<br>
- Shared Room: <b>฿{md['room_types']['Shared Room']['median_price']:,}</b> median<br><br>
<b>Top Neighbourhoods by Price:</b><br>
{top5_nb}<br>
<i>💡 Entire homes command a <b>38% premium</b> over private rooms — statistically significant (p&lt;0.0001, Mann-Whitney U, r=0.29)</i>"""

    elif any(w in q for w in ["neighbourhood", "area", "location", "district", "zone"]):
        nb_html = "".join([
            f"• <b>{nb}</b>: {data['listings']:,} listings · ฿{data['median_price']:,} median<br>"
            for nb, data in md["top_neighbourhoods"].items()
        ])
        return f"""<b>Bangkok Neighbourhood Analysis</b><br><br>
<b>Top Neighbourhoods by Supply:</b><br>
{nb_html}<br>
<b>Premium Pricing Zones:</b><br>
- Parthum Wan: ฿2,225 median (highest priced — central CBD)<br>
- Bang Rak: ฿1,890 median (riverside + business district)<br>
- Vadhana: ฿1,828 median (Sukhumvit corridor — highest supply)<br><br>
<b>Statistical Finding:</b><br>
- Neighbourhood explains <b>10.5% of price variance</b><br>
- Kruskal-Wallis H=1,726.68, p&lt;0.0001, η²=0.1055 (moderate effect)<br>
- Price range across neighbourhoods: ฿581 (Nong Khaem) to ฿2,225 (Parthum Wan)<br><br>
<i>💡 Investment tip: Bang Rak offers the best combination of pricing power (฿1,890) and market liquidity</i>"""

    elif any(w in q for w in ["host", "superhost", "owner", "operator"]):
        return f"""<b>Bangkok Host Market Intelligence</b><br><br>
<b>Market Structure:</b><br>
- Total unique hosts: <b>{md['unique_hosts']:,}</b><br>
- Superhosts: <b>{md['superhost_count']:,}</b> (89.9% of hosts)<br>
- Commercial operators (6+ listings): <b>10.6%</b> of hosts<br>
- Commercial supply control: <b>{md['commercial_pct']}%</b> of all listings<br>
- Top single host: <b>243 listings</b><br><br>
<b>Superhost Revenue Premium:</b><br>
- Superhost median annual revenue: <b>฿{md['superhost_revenue']:,}</b><br>
- Non-superhost median annual revenue: <b>฿{md['non_superhost_revenue']:,}</b><br>
- Revenue gap: <b>+340%</b> for superhosts<br><br>
<b>Superhost Quality Signal:</b><br>
- Superhost avg rating: <b>{md['superhost_rating']}</b> vs {md['non_superhost_rating']} (Cohen's d=0.54)<br>
- Price difference: minimal (฿1,390 vs ฿1,371)<br><br>
<i>💡 Superhosts earn more through <b>higher occupancy</b>, not higher prices — quality drives demand</i>"""

    elif any(w in q for w in ["occupancy", "booking", "demand", "available", "season"]):
        monthly_html = "".join([
            f"• {month}: <b>{occ}%</b>{'  ← PEAK' if occ > 40 else '  ← LOW' if occ < 25 else ''}<br>"
            for month, occ in md["monthly_occupancy"].items()
        ])
        return f"""<b>Bangkok Occupancy & Demand Analysis</b><br><br>
<b>Overall Metrics:</b><br>
- Mean occupancy rate: <b>{md['avg_occupancy']:.1%}</b><br>
- Median occupancy rate: <b>{md['median_occupancy']:.1%}</b><br><br>
<b>By Room Type:</b><br>
- Hotel Room: <b>37.5%</b> (highest)<br>
- Private Room: <b>32.7%</b><br>
- Entire Home: <b>31.1%</b><br>
- Shared Room: <b>11.6%</b> (lowest)<br><br>
<b>Monthly Seasonality:</b><br>
{monthly_html}<br>
<b>Market Recovery:</b><br>
- 2024 reviews: <b>148,869</b> (all-time high)<br>
- vs 2019 pre-COVID: <b>+152%</b> growth<br><br>
<i>💡 Weekend vs weekday: <b>No significant difference</b> (p=0.526) — Bangkok is tourist-driven, not business travel</i>"""

    elif any(w in q for w in ["review", "rating", "score", "sentiment", "clean", "guest"]):
        return f"""<b>Bangkok Review & Rating Analysis</b><br><br>
<b>Overall Ratings:</b><br>
- Mean rating: <b>{md['mean_rating']} / 5.00</b><br>
- Listings rated above 4.5: <b>{md['pct_above_4_5']}%</b> — rating inflation confirmed<br>
- Total reviews analyzed: <b>{md['total_reviews']:,}</b><br><br>
<b>Sentiment Analysis (VADER, n=50,000):</b><br>
- Positive: <b>{md['nlp_results']['positive_pct']}%</b><br>
- Neutral: {md['nlp_results']['neutral_pct']}%<br>
- Negative: {md['nlp_results']['negative_pct']}%<br><br>
<b>Sub-dimension Scores (lowest → highest):</b><br>
- Value: 4.65 → Location: 4.66 → Cleanliness: 4.68<br>
- Accuracy: 4.72 → Check-in: 4.76 → Communication: 4.78<br><br>
<b>NLP Insights:</b><br>
- Top landmark: <b>{md['nlp_results']['top_landmark']}</b><br>
- Top amenity: <b>{md['nlp_results']['top_amenity']}</b><br>
- Top complaint: <b>{md['nlp_results']['top_complaint']}</b><br>
- Informative reviews: {md['nlp_results']['informative_pct']}% · Superficial: {md['nlp_results']['superficial_pct']}%<br><br>
<i>💡 40% of reviews are non-English (German, Spanish, French) — multilingual NLP needed for full coverage</i>"""

    elif any(w in q for w in ["revenue", "income", "earn", "profit", "money"]):
        amenity_html = "".join([
            f"• {amenity}: <b>+{premium}%</b> price premium<br>"
            for amenity, premium in list(md["amenity_premiums"].items())[:6]
        ])
        return f"""<b>Bangkok Airbnb Revenue Analysis</b><br><br>
<b>Market Revenue Metrics:</b><br>
- Median estimated annual revenue: <b>฿{md['median_annual_revenue']:,}</b> (~$1,700 USD)<br>
- Mean estimated annual revenue: <b>฿{md['mean_annual_revenue']:,}</b> (~$5,600 USD)<br><br>
<b>Revenue by Host Type:</b><br>
- Superhost median: <b>฿{md['superhost_revenue']:,}</b><br>
- Non-superhost median: <b>฿{md['non_superhost_revenue']:,}</b><br>
- Revenue gap: <b>+340%</b> for superhosts<br><br>
<b>Amenity Price Premiums:</b><br>
{amenity_html}<br>
<b>Revenue Optimization Opportunities:</b><br>
- Weekend pricing premium: currently <b>฿0</b> (missed opportunity)<br>
- Peak season (Jul–Sep): 43% occupancy vs 24% trough<br>
- Superhost status: single biggest revenue lever (+340%)<br><br>
<i>💡 The median host earns ~฿5,154/month — meaningful supplementary income but not primary livelihood for most</i>"""

    elif any(w in q for w in ["ml", "model", "predict", "machine learning", "algorithm"]):
        results_html = "".join([
            f"• <b>{model}</b>: MAE=฿{res['MAE']:,} · R²={res['R2']} · MAPE={res['MAPE']}%<br>"
            for model, res in md["ml_results"].items()
        ])
        features_html = "".join([
            f"• <b>{feat}</b>: {imp}% importance<br>"
            for feat, imp in md["top_features"]
        ])
        return f"""<b>ML Price Prediction Results</b><br><br>
<b>Model Comparison (5-Fold Cross-Validation):</b><br>
{results_html}<br>
<b>Winner: Gradient Boosting</b> (R²=0.662, MAE=฿504, MAPE=29.1%)<br><br>
<b>Top Feature Importances:</b><br>
{features_html}<br>
<b>Model Performance:</b><br>
- 72.2% of predictions within ฿500 of actual price<br>
- 87.3% within ฿1,000<br>
- Mean residual: ฿180 (slight underprediction)<br><br>
<b>Bias Analysis:</b><br>
- Best: Phra Khanong (MAE=฿350)<br>
- Worst: Bang Rak (MAE=฿632) — premium segment harder to predict<br><br>
<i>💡 Price is driven by non-linear combinations of location + size — Ridge regression (linear) performs 30% worse than tree-based models</i>"""

    elif any(w in q for w in ["statistic", "hypothesis", "test", "significant", "pvalue"]):
        hyp_html = "".join([
            f"• <b>{hid}</b>: {res['result']} (p={res['pvalue']}, {res['effect']}) — {res['finding']}<br>"
            for hid, res in md["hypothesis_results"].items()
        ])
        return f"""<b>Statistical Analysis Results</b><br><br>
<b>Hypothesis Testing Summary:</b><br>
{hyp_html}<br>
<b>Key Statistical Notes:</b><br>
- All price variables confirmed non-normal (Shapiro-Wilk p&lt;0.0001)<br>
- Non-parametric tests used throughout (Mann-Whitney U, Kruskal-Wallis)<br>
- Effect sizes reported alongside p-values — critical at large n<br><br>
<b>OLS Regression Results:</b><br>
- R²=0.455 (full model) · R²=0.342 (after VIF correction)<br>
- availability_365 VIF=65 — severe multicollinearity with occupancy_rate<br>
- neighbourhood_median_price strongest legitimate predictor<br><br>
<i>💡 H3 lesson: With n=23,039, even ฿41 differences achieve p&lt;0.00001. Always report effect sizes, not just p-values.</i>"""

    elif any(w in q for w in ["recommend", "suggest", "improve", "tip", "advice", "should"]):
        return f"""<b>Market Intelligence Recommendations</b><br><br>
<b>For Hosts:</b><br>
- Pursue Superhost status → revenue jumps from ฿{md['non_superhost_revenue']:,} to ฿{md['superhost_revenue']:,} (+340%)<br>
- Implement weekend pricing premium — Bangkok has <b>zero competition</b> currently (H5: p=0.526)<br>
- Highlight BTS/MRT proximity — mentioned in <b>2,513 reviews</b>, #1 booking driver<br>
- Upgrade amenities: TV (+68.6%), Hot tub (+49.8%), Kitchen (+36.9%)<br>
- Dynamic pricing for Jul–Sep peak season (43% vs 24% Feb trough)<br><br>
<b>For Investors:</b><br>
- Bangkok market at all-time high — 2024 reviews +152% vs 2019 pre-COVID<br>
- Target Bang Rak (฿1,890) / Vadhana (฿1,828) for premium positioning<br>
- Mid-market ฿1,000–2,500 captures peak demand concentration<br>
- High Demand host segment achieves <b>61% occupancy</b><br><br>
<b>For Platform Operators:</b><br>
- Monitor commercial concentration — 10.6% of hosts control 57% of supply<br>
- Address rating inflation — 81.4% above 4.5 compresses signal value<br>
- Deploy multilingual NLP — 40% of reviews are non-English<br><br>
<i>💡 Biggest opportunity: Bangkok's zero weekend pricing premium = immediate revenue upside for early adopters</i>"""

    elif any(w in q for w in ["dataset", "data", "about", "what", "tell", "info", "overview"]):
        return f"""<b>About This Analysis</b><br><br>
<b>Dataset: Inside Airbnb — Bangkok, Thailand</b><br>
- Scrape date: September 2025<br>
- Listings: <b>{md['total_listings']:,}</b> active listings<br>
- Hosts: <b>{md['unique_hosts']:,}</b> unique hosts<br>
- Neighbourhoods: <b>{md['neighbourhoods']}</b><br>
- Reviews: <b>{md['total_reviews']:,}</b> guest reviews<br>
- Calendar records: <b>10,514,202</b> (365 days forward)<br><br>
<b>Analysis Pipeline:</b><br>
- Ingestion → Profiling → Cleaning → Enrichment → Star Schema<br>
- EDA → Hypothesis Testing → ML → NLP → RAG → Dashboard<br><br>
<b>Tools Used:</b><br>
- Python, pandas, DuckDB, scikit-learn, VADER, plotly, Streamlit<br>
- dbt models, Docker, AWS architecture design<br><br>
<b>GitHub:</b> github.com/primemarasinghe/airbnb-market-intelligence<br><br>
<i>💡 Ask me about: prices, neighbourhoods, hosts, occupancy, reviews, revenue, ML models, or recommendations</i>"""

    else:
        return f"""<b>Bangkok Airbnb Market Intelligence</b><br><br>
I can answer questions about the Bangkok short-term rental market based on analysis of {md['total_listings']:,} listings.<br><br>
<b>Try asking about:</b><br>
- 💰 <b>Pricing</b> — "What are the prices in Bangkok?"<br>
- 📍 <b>Neighbourhoods</b> — "Which areas are most popular?"<br>
- 🏠 <b>Hosts</b> — "How do superhosts perform?"<br>
- 📈 <b>Demand</b> — "When is peak season?"<br>
- ⭐ <b>Reviews</b> — "What do guests say about cleanliness?"<br>
- 💵 <b>Revenue</b> — "How much can I earn?"<br>
- 🤖 <b>ML Models</b> — "How accurate is the price prediction?"<br>
- 📊 <b>Statistics</b> — "What did the hypothesis tests show?"<br>
- 💡 <b>Recommendations</b> — "What should hosts do to improve?"<br><br>
<i>This AI analyst is powered by real market data from the Inside Airbnb Bangkok dataset (Sep 2025)</i>"""

# --- UI ---
st.markdown("""
<div style="background:linear-gradient(135deg,#1a1f2e,#0e1117);border-bottom:1px solid #00d4ff;padding:1.5rem 0 1rem 0;margin-bottom:1.5rem;">
    <h1 style="font-family:'DM Serif Display',serif;color:white;margin:0;font-size:1.8rem;">
        🤖 Bangkok Airbnb AI Analyst
    </h1>
    <p style="color:#7a8499;margin:0.3rem 0 0 0;font-size:0.85rem;">
        Powered by analysis of 28,806 listings · 583,333 reviews · Sep 2025 · No data files required
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 📊 Market Snapshot")
st.sidebar.metric("Total Listings", "28,806")
st.sidebar.metric("Median Price", "฿1,359/night")
st.sidebar.metric("Avg Occupancy", "31.5%")
st.sidebar.metric("2024 Reviews", "148,869 (ATH)")
st.sidebar.divider()

st.sidebar.markdown("### 💡 Try asking:")
suggestions = [
    "What are the prices in Bangkok?",
    "Which neighbourhoods are most popular?",
    "How do superhosts perform?",
    "What is the peak season?",
    "What do reviews say about cleanliness?",
    "How much revenue can I earn?",
    "What do the ML models show?",
    "What should hosts do to improve?",
    "Tell me about this dataset"
]

for s in suggestions:
    if st.sidebar.button(s, use_container_width=True, key=f"btn_{s[:20]}"):
        if not any(m["content"] == s for m in st.session_state.get("messages", [])[-2:]):
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append({"role": "user", "content": s})
            response = answer_question(s)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Initialize messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"""<b>Welcome to the Bangkok Airbnb Market Intelligence Analyst!</b><br><br>
I have deep knowledge of <b>28,806 listings</b>, <b>583,333 reviews</b>, and <b>10.5M calendar records</b> from the Bangkok Inside Airbnb dataset (September 2025).<br><br>
I can answer questions about pricing, neighbourhoods, hosts, demand, reviews, revenue, ML models, and business recommendations.<br><br>
<i>Use the sidebar buttons or type your own question below.</i>"""
    })

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user"><div class="chat-user-bubble">{msg["content"]}</div></div>',
                   unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="chat-assistant">
            <div class="chat-avatar">🤖</div>
            <div class="chat-assistant-bubble">{msg["content"]}</div>
        </div>""", unsafe_allow_html=True)

# Input
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("Ask about the Bangkok Airbnb market...",
                                key="user_input",
                                label_visibility="collapsed")
with col2:
    send = st.button("Send", use_container_width=True)

if send and st.session_state.get("user_input"):
    question = st.session_state.user_input
    st.session_state.messages.append({"role": "user", "content": question})
    response = answer_question(question)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

if st.button("Clear conversation", key="clear"):
    st.session_state.messages = []
    st.rerun()

st.markdown("""
<div style="text-align:center;color:#3a4050;font-size:0.75rem;padding:2rem 0 0.5rem 0;">
    Built by Primesh Marasinghe · Inside Airbnb Bangkok Sep 2025 · Expernetic Data Engineer Assessment
</div>
""", unsafe_allow_html=True)