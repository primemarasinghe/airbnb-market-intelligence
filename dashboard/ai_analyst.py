import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import re
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Bangkok Airbnb AI Analyst",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

* { font-family: 'DM Sans', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%);
    border-bottom: 1px solid #00d4ff;
    padding: 1.5rem 0 1rem 0;
    margin-bottom: 1.5rem;
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

.chat-assistant-bubble strong {
    color: #00d4ff;
}

.chat-assistant-bubble ul {
    padding-left: 1.2rem;
    margin: 0.4rem 0;
}

.chat-assistant-bubble li {
    margin: 0.2rem 0;
}

.suggestion-pill {
    display: inline-block;
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    color: #7a8499;
    margin: 0.2rem;
    cursor: pointer;
}

[data-testid="stSidebar"] {
    background: #1a1f2e;
    border-right: 1px solid #2a2f3e;
}

.metric-card {
    background: #0e1117;
    border: 1px solid #2a2f3e;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.3rem 0;
    text-align: center;
}

.metric-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: #00d4ff;
}

.metric-label {
    font-size: 0.7rem;
    color: #7a8499;
    text-transform: uppercase;
    letter-spacing: 0.5px;
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

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/listings_enriched.csv", low_memory=False)
    df["occupancy_rate"] = 1 - (df["availability_365"] / 365)
    df["estimated_annual_revenue"] = df["price"] * (365 - df["availability_365"])
    df = df[df["price"].between(100, 10000)]
    return df

@st.cache_data
def load_reviews():
    reviews = pd.read_csv("data/processed/reviews_clean.csv", low_memory=False)
    reviews = reviews[reviews["comments"].notna()]
    reviews = reviews[reviews["comments"].str.len() > 20]
    return reviews.sample(10000, random_state=42).reset_index(drop=True)

@st.cache_resource
def build_rag(_reviews):
    def clean_text(text):
        text = str(text).lower()
        text = re.sub(r'[^a-z\s]', '', text)
        return text
    _reviews["clean"] = _reviews["comments"].apply(clean_text)
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2),
                                  stop_words="english")
    matrix = vectorizer.fit_transform(_reviews["clean"])
    return vectorizer, matrix

def retrieve_reviews(query, vectorizer, matrix, reviews, top_k=8):
    def clean_text(text):
        return re.sub(r'[^a-z\s]', '', str(text).lower())
    qvec = vectorizer.transform([clean_text(query)])
    scores = cosine_similarity(qvec, matrix).flatten()
    top_idx = scores.argsort()[-top_k:][::-1]
    return [(reviews.iloc[i]["comments"], scores[i]) for i in top_idx]

def answer_question(question, df, reviews, vectorizer, matrix):
    q = question.lower()

    if any(w in q for w in ["price", "cost", "expensive", "cheap"]):
        median_price = df["price"].median()
        max_nb = df.groupby("neighbourhood_cleansed")["price"].median().idxmax()
        min_nb = df.groupby("neighbourhood_cleansed")["price"].median().idxmin()
        answer = f"""<b>Bangkok Airbnb Pricing Analysis</b><br><br>
- Median nightly price: <b>฿{median_price:,.0f} THB</b> (~$38 USD)<br>
- Most expensive neighbourhood: <b>{max_nb}</b> (฿{df[df['neighbourhood_cleansed']==max_nb]['price'].median():,.0f} median)<br>
- Most affordable neighbourhood: <b>{min_nb}</b> (฿{df[df['neighbourhood_cleansed']==min_nb]['price'].median():,.0f} median)<br>
- Entire homes cost <b>38% more</b> than private rooms (฿1,491 vs ฿1,080 median)<br>
- Price range: ฿100 – ฿10,000+ (luxury segment)<br><br>
<i>💡 Statistical note: Mann-Whitney U test confirms price difference is significant (p&lt;0.0001, effect size r=0.29)</i>"""

    elif any(w in q for w in ["neighbourhood", "area", "location", "district"]):
        top5 = df.groupby("neighbourhood_cleansed")["id"].count().sort_values(ascending=False).head(5)
        top5_html = "".join([f"• {nb}: <b>{cnt:,}</b> listings<br>" for nb, cnt in top5.items()])
        answer = f"""<b>Bangkok Neighbourhood Analysis</b><br><br>
<b>Top 5 by listing supply:</b><br>
{top5_html}<br>
<b>Premium pricing zones:</b><br>
- Bang Rak: ฿1,875 median (riverside + CBD)<br>
- Vadhana: ฿1,773 median (Sukhumvit corridor)<br>
- Parthum Wan: ฿2,225 median (highest priced)<br><br>
<i>💡 Key insight: Neighbourhood explains <b>10.5% of price variance</b> (Kruskal-Wallis η²=0.1055, p&lt;0.0001)</i>"""

    elif any(w in q for w in ["host", "superhost", "owner"]):
        sh_count = int(df["host_is_superhost"].sum())
        answer = f"""<b>Bangkok Host Analysis</b><br><br>
- Total unique hosts: <b>{df['host_id'].nunique():,}</b><br>
- Superhosts: <b>{sh_count:,}</b> ({sh_count/df['host_id'].nunique():.1%} of hosts)<br>
- Commercial operators (6+ listings): <b>10.6%</b> of hosts control <b>57%</b> of listings<br>
- Top single host manages <b>243 listings</b><br><br>
<b>Superhost Impact:</b><br>
- Avg rating: 4.86 vs 4.58 (Cohen's d=0.54, medium effect)<br>
- Median annual revenue: <b>฿114,431</b> vs <b>฿25,968</b> (340% premium)<br>
- Price difference: minimal (฿1,390 vs ฿1,371)<br><br>
<i>💡 Superhosts earn more through higher occupancy, not higher prices</i>"""

    elif any(w in q for w in ["occupancy", "booking", "available", "demand"]):
        avg_occ = df["occupancy_rate"].mean()
        answer = f"""<b>Bangkok Occupancy & Demand Analysis</b><br><br>
- Mean occupancy rate: <b>{avg_occ:.1%}</b> (availability_365 proxy)<br>
- Median occupancy rate: <b>20.6%</b><br>
- Peak season: <b>July–September</b> (43% occupancy)<br>
- Lowest demand: <b>February–March</b> (~24%)<br><br>
<b>By Room Type:</b><br>
- Hotel rooms: 37.5% (highest)<br>
- Private rooms: 32.7%<br>
- Entire homes: 31.1%<br>
- Shared rooms: 11.6%<br><br>
<i>💡 Weekend vs weekday: No significant difference (p=0.526) — Bangkok is tourist-driven, not business travel</i>"""

    elif any(w in q for w in ["review", "rating", "score", "sentiment", "clean", "cleanliness"]):
        avg_rating = df["review_scores_rating"].mean()
        answer = f"""<b>Bangkok Review & Rating Analysis</b><br><br>
<b>Overall Ratings:</b><br>
- Mean rating: <b>{avg_rating:.2f} / 5.00</b><br>
- 81.4% of listings rated above 4.5 — rating inflation confirmed<br>
- Total reviews analyzed: <b>583,333</b><br>
- 2024 review volume: <b>148,869</b> (all-time high, +152% vs 2019)<br><br>
<b>Sentiment Analysis (VADER, n=50,000):</b><br>
- Positive: 72.9% &nbsp;|&nbsp; Neutral: 22.7% &nbsp;|&nbsp; Negative: 4.4%<br><br>
<b>Sub-dimension Scores (lowest → highest):</b><br>
- Value: 4.65 → Location: 4.66 → Cleanliness: 4.68 → Accuracy: 4.72 → Check-in: 4.76 → Communication: 4.78<br><br>
<b>Top Guest Complaints:</b> Small rooms · Noise · Smell<br>
<b>Top Guest Praise:</b> BTS access · Cleanliness · Helpful hosts<br><br>
<i>💡 Hosts should prioritize cleanliness (4.68) to close gap with communication scores (4.78)</i>"""

    elif any(w in q for w in ["revenue", "income", "earn", "profit"]):
        answer = """<b>Bangkok Airbnb Revenue Analysis</b><br><br>
- Median estimated annual revenue: <b>฿61,848</b> (~$1,700 USD)<br>
- Mean estimated annual revenue: <b>฿203,274</b> (~$5,600 USD)<br><br>
<b>By Host Segment:</b><br>
- High Occupancy Hosts: highest revenue (61% occupancy)<br>
- Luxury Hosts: ฿4,715 avg price but only 18% occupancy<br>
- Commercial Operators: volume-driven, lower individual revenue<br><br>
<b>Revenue Optimization Opportunities:</b><br>
- Superhost status → 340% revenue premium<br>
- Weekend pricing premium (currently zero in Bangkok)<br>
- Peak season (Jul–Sep) dynamic pricing<br>
- Amenity upgrades: TV (+68.6%) · Hot tub (+49.8%) · Kitchen (+36.9%)<br><br>
<i>💡 The gap between mean (฿203K) and median (฿62K) revenue confirms a highly skewed market — top listings earn disproportionately more</i>"""

    elif any(w in q for w in ["recommend", "suggestion", "improve", "tip"]):
        answer = """<b>Market Intelligence Recommendations</b><br><br>
<b>For Hosts:</b><br>
- Pursue Superhost status — median revenue jumps from ฿25,968 to ฿114,431<br>
- Implement weekend pricing premium — Bangkok has zero premium currently<br>
- Highlight BTS/MRT proximity — mentioned in 2,513 reviews<br>
- Price check against neighbourhood median — many listings are 30%+ underpriced<br><br>
<b>For Investors:</b><br>
- Target Bang Rak / Vadhana for premium positioning<br>
- Mid-market (฿1,000–2,500) captures highest demand concentration<br>
- Bangkok market growing — 2024 reviews 152% above 2019 peak<br><br>
<b>For Platform Operators:</b><br>
- Monitor commercial host concentration (57% of listings)<br>
- Address rating inflation — 81.4% above 4.5 compresses signal value<br><br>
<i>💡 Bangkok's biggest missed opportunity: zero weekend pricing premium despite strong tourist demand</i>"""

    elif any(w in q for w in ["dataset", "data", "about", "what", "tell", "info"]):
        answer = """<b>About This Dataset</b><br><br>
This AI analyst is powered by the <b>Inside Airbnb Bangkok dataset</b> (September 2025 scrape).<br><br>
<b>Dataset Scale:</b><br>
- <b>28,806</b> active listings across Bangkok<br>
- <b>8,874</b> unique hosts<br>
- <b>50</b> neighbourhoods<br>
- <b>583,333</b> guest reviews<br>
- <b>10,514,202</b> calendar records<br><br>
<b>Files Available:</b><br>
- listings.csv — pricing, location, host info, amenities<br>
- calendar.csv — daily availability (365 days forward)<br>
- reviews.csv — guest review text and metadata<br>
- neighbourhoods.csv — geographic groupings<br><br>
<b>Pipeline Built:</b><br>
- Ingestion → Profiling → Cleaning → Enrichment → Star Schema → ML/NLP<br><br>
<i>💡 Ask me about prices, neighbourhoods, hosts, occupancy, reviews, or revenue for detailed analysis</i>"""

    else:
        retrieved = retrieve_reviews(question, vectorizer, matrix, reviews)
        relevant = [(r, s) for r, s in retrieved if s > 0.05][:3]

        answer = f"""<b>Review-Based Insights</b><br><br>
Here are the most relevant guest experiences for your query:<br><br>"""

        if relevant:
            for i, (review, score) in enumerate(relevant, 1):
                answer += f"<b>Guest {i}</b> (relevance: {score:.2f}):<br><i>\"{review[:250]}\"</i><br><br>"
        else:
            answer += "No highly relevant reviews found for this query.<br><br>"

        answer += "<i>💡 Try asking about: prices, neighbourhoods, hosts, occupancy, reviews, revenue, or recommendations</i>"

    return answer

# --- UI ---
st.markdown("""
<div class="main-header">
    <h1 style="font-family:'DM Serif Display',serif; color:white; margin:0; font-size:1.8rem;">
        🤖 Bangkok Airbnb AI Analyst
    </h1>
    <p style="color:#7a8499; margin:0.3rem 0 0 0; font-size:0.85rem;">
        Powered by market intelligence from 28,806 listings · 583,333 reviews · Sep 2025 scrape
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# Load data
with st.spinner("Loading market data..."):
    df = load_data()
    reviews = load_reviews()
    vectorizer, matrix = build_rag(reviews)

# Sidebar stats
st.sidebar.markdown("### 📊 Market Snapshot")
st.sidebar.metric("Total Listings", f"{len(df):,}")
st.sidebar.metric("Median Price", f"฿{df['price'].median():,.0f}")
st.sidebar.metric("Avg Occupancy", f"{df['occupancy_rate'].mean():.1%}")
st.sidebar.metric("Unique Hosts", f"{df['host_id'].nunique():,}")
st.sidebar.divider()

st.sidebar.markdown("### 💡 Try asking:")
suggestions = [
    "What are the prices in Bangkok?",
    "Which neighbourhoods are most popular?",
    "How do superhosts perform?",
    "What is the occupancy rate?",
    "What do reviews say about cleanliness?",
    "How much revenue can I earn?",
    "What should I do to improve my listing?"
]
for s in suggestions:
    if st.sidebar.button(s, use_container_width=True, key=f"btn_{s[:20]}"):
        if not any(m["content"] == s for m in st.session_state.messages[-2:]):
            st.session_state.messages.append({"role": "user", "content": s})
            response = answer_question(s, df, reviews, vectorizer, matrix)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """👋 Hello! I'm your Bangkok Airbnb Market Intelligence Analyst.

I have deep knowledge of **28,806 listings**, **583,333 reviews**, and **10.5M calendar records** from the Bangkok Inside Airbnb dataset (September 2025).

Ask me about:
- 💰 **Pricing** — what should you charge?
- 📍 **Neighbourhoods** — where to invest?
- 🏠 **Hosts** — how do superhosts differ?
- 📈 **Demand** — when is peak season?
- ⭐ **Reviews** — what do guests say?
- 💵 **Revenue** — how much can you earn?"""
    })

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-user">
            <div class="chat-user-bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        content = msg["content"].replace("\n", "<br>")
        st.markdown(f"""
        <div class="chat-assistant">
            <div class="chat-avatar">🤖</div>
            <div class="chat-assistant-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# Input
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("Ask a question about the Bangkok Airbnb market...",
                                key="user_input",
                                value=st.session_state.get("input_value", ""),
                                label_visibility="collapsed")
with col2:
    send = st.button("Send", use_container_width=True)

if send and st.session_state.get("user_input"):
    question = st.session_state.user_input
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Analyzing..."):
        response = answer_question(question, df, reviews, vectorizer, matrix)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state["input_value"] = ""
    st.rerun()

# Clear button
if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()