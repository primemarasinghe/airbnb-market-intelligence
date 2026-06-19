import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Bangkok Airbnb Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}

.main-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #0e1117 100%);
    border-left: 4px solid #00d4ff;
    padding: 2rem 2rem 1.5rem 2rem;
    margin-bottom: 2rem;
    border-radius: 0 12px 12px 0;
}

.main-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
}

.main-header p {
    color: #7a8499;
    font-size: 0.9rem;
    margin: 0.4rem 0 0 0;
    font-weight: 300;
}

.kpi-card {
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
}

.kpi-card:hover { border-color: #00d4ff; }

.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #00d4ff;
    line-height: 1;
}

.kpi-label {
    font-size: 0.75rem;
    color: #7a8499;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.4rem;
}

.kpi-delta {
    font-size: 0.8rem;
    color: #4ade80;
    margin-top: 0.2rem;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    border-bottom: 1px solid #2a2f3e;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.insight-box {
    background: #1a1f2e;
    border-left: 3px solid #00d4ff;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
    color: #b0b8cc;
    margin-top: 0.5rem;
}

[data-testid="stSidebar"] {
    background-color: #1a1f2e;
    border-right: 1px solid #2a2f3e;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {
    color: #7a8499 !important;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div[data-testid="metric-container"] {
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 12px;
    padding: 1rem;
}

.stPlotlyChart { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="#1a1f2e",
        plot_bgcolor="#1a1f2e",
        font=dict(color="#e0e0e0", family="Inter"),
        colorway=["#00d4ff", "#ff6b6b", "#4ade80", "#f59e0b", "#a78bfa"],
        xaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e"),
        yaxis=dict(gridcolor="#2a2f3e", linecolor="#2a2f3e"),
        legend=dict(bgcolor="#1a1f2e"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
)

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/listings_enriched.csv", low_memory=False)
    df["occupancy_rate"] = 1 - (df["availability_365"] / 365)
    df["estimated_annual_revenue"] = df["price"] * (365 - df["availability_365"])
    df = df[df["price"].between(1, 50000)]
    return df

df = load_data()

# --- Sidebar ---
st.sidebar.markdown("### 🔍 Market Filters")
room_types = st.sidebar.multiselect(
    "Room Type",
    options=df["room_type"].unique().tolist(),
    default=df["room_type"].unique().tolist()
)
price_range = st.sidebar.slider("Price Range (THB)", 0, 10000, (0, 5000))
neighbourhoods = st.sidebar.multiselect(
    "Neighbourhood",
    options=sorted(df["neighbourhood_cleansed"].dropna().unique().tolist()),
    default=[]
)
superhost_only = st.sidebar.checkbox("Superhost Only")

filtered = df[
    (df["room_type"].isin(room_types)) &
    (df["price"].between(price_range[0], price_range[1]))
]
if neighbourhoods:
    filtered = filtered[filtered["neighbourhood_cleansed"].isin(neighbourhoods)]
if superhost_only:
    filtered = filtered[filtered["host_is_superhost"] == True]

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🏙️ Bangkok Airbnb Intelligence</h1>
    <p>Inside Airbnb · September 2025 Scrape · 28,806 Listings · 50 Neighbourhoods</p>
</div>
""", unsafe_allow_html=True)

# --- KPIs ---
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, f"{len(filtered):,}", "Listings"),
    (k2, f"฿{filtered['price'].median():,.0f}", "Median Price / Night"),
    (k3, f"{filtered['occupancy_rate'].mean():.1%}", "Avg Occupancy"),
    (k4, f"{filtered['host_id'].nunique():,}", "Unique Hosts"),
    (k5, f"฿{filtered['estimated_annual_revenue'].median():,.0f}", "Median Annual Revenue"),
]
for col, val, label in kpis:
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{val}</div>
        <div class="kpi-label">{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Row 1: Price & Room Type ---
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="section-title">Price Distribution by Room Type</div>', unsafe_allow_html=True)
    fig = px.violin(
        filtered[filtered["price"] < 5000],
        x="room_type", y="price", color="room_type",
        box=True, template=PLOTLY_TEMPLATE,
        labels={"price": "Price (THB)", "room_type": ""}
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">💡 Entire homes command a 38% price premium over private rooms (฿1,491 vs ฿1,080 median), confirmed statistically significant with p&lt;0.0001.</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">Market Composition</div>', unsafe_allow_html=True)
    counts = filtered["room_type"].value_counts().reset_index()
    fig = px.pie(
        counts, names="room_type", values="count",
        hole=0.6, template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#00d4ff","#ff6b6b","#4ade80","#f59e0b"]
    )
    fig.update_layout(height=350, legend=dict(orientation="h", y=-0.1))
    fig.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

# --- Row 2: Neighbourhoods ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Top Neighbourhoods by Median Price</div>', unsafe_allow_html=True)
    n_price = filtered.groupby("neighbourhood_cleansed")["price"].median().sort_values(ascending=True).tail(15).reset_index()
    fig = px.bar(
        n_price, x="price", y="neighbourhood_cleansed",
        orientation="h", template=PLOTLY_TEMPLATE,
        labels={"price": "Median Price (THB)", "neighbourhood_cleansed": ""},
        color="price", color_continuous_scale=["#1a1f2e","#00d4ff"]
    )
    fig.update_layout(height=400, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">Top Neighbourhoods by Supply</div>', unsafe_allow_html=True)
    n_count = filtered["neighbourhood_cleansed"].value_counts().head(15).reset_index()
    fig = px.bar(
        n_count, x="count", y="neighbourhood_cleansed",
        orientation="h", template=PLOTLY_TEMPLATE,
        labels={"count": "Listings", "neighbourhood_cleansed": ""},
        color="count", color_continuous_scale=["#1a1f2e","#ff6b6b"]
    )
    fig.update_layout(height=400, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

# --- Row 3: Host & Occupancy ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="section-title">Host Market Structure</div>', unsafe_allow_html=True)
    host_type = filtered["host_type"].value_counts().reset_index()
    fig = px.pie(
        host_type, names="host_type", values="count",
        hole=0.55, template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#4ade80","#f59e0b","#ff6b6b"]
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">⚠️ 57% of listings are controlled by commercial operators (6+ listings).</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">Occupancy by Room Type</div>', unsafe_allow_html=True)
    occ = filtered.groupby("room_type")["occupancy_rate"].mean().reset_index()
    fig = px.bar(
        occ, x="room_type", y="occupancy_rate",
        template=PLOTLY_TEMPLATE, color="room_type",
        labels={"occupancy_rate": "Avg Occupancy", "room_type": ""},
        color_discrete_sequence=["#00d4ff","#ff6b6b","#4ade80","#f59e0b"]
    )
    fig.update_layout(showlegend=False, height=300, yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown('<div class="section-title">Superhost Impact</div>', unsafe_allow_html=True)
    sh = filtered.groupby("host_is_superhost").agg(
        avg_rating=("review_scores_rating","mean"),
        median_price=("price","median"),
        count=("id","count")
    ).reset_index()
    sh["label"] = sh["host_is_superhost"].map({True:"Superhost", False:"Non-Superhost"})
    fig = px.bar(
        sh, x="label", y="avg_rating",
        template=PLOTLY_TEMPLATE,
        color="label",
        labels={"avg_rating":"Avg Rating","label":""},
        color_discrete_sequence=["#7a8499","#f59e0b"]
    )
    fig.update_layout(showlegend=False, height=300, yaxis=dict(range=[4.0, 5.0]))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight-box">⭐ Superhosts rate 0.28 points higher (4.86 vs 4.58), Cohen\'s d=0.54.</div>', unsafe_allow_html=True)

# --- Map ---
st.markdown('<div class="section-title">📍 Listing Density & Price Map</div>', unsafe_allow_html=True)
map_df = filtered[["latitude","longitude","price","room_type","neighbourhood_cleansed"]].dropna()
map_df = map_df[map_df["price"] < 10000].sample(min(4000, len(map_df)), random_state=42)

fig = px.scatter_mapbox(
    map_df, lat="latitude", lon="longitude",
    color="price", size_max=6,
    color_continuous_scale="plasma",
    mapbox_style="carto-darkmatter",
    zoom=10.5, center={"lat": 13.75, "lon": 100.5},
    hover_data=["room_type","neighbourhood_cleansed","price"],
    opacity=0.7,
    labels={"price":"Price (THB)"}
)
fig.update_layout(
    height=500,
    paper_bgcolor="#1a1f2e",
    margin=dict(l=0,r=0,t=0,b=0)
)
st.plotly_chart(fig, use_container_width=True)

# --- Review Trends ---
st.markdown('<div class="section-title">📈 Market Growth — Review Volume by Year</div>', unsafe_allow_html=True)

@st.cache_data
def load_reviews():
    reviews = pd.read_csv("data/processed/reviews_clean.csv", low_memory=False)
    reviews["date"] = pd.to_datetime(reviews["date"])
    reviews["year"] = reviews["date"].dt.year
    return reviews

reviews = load_reviews()
yearly = reviews[reviews["year"].between(2015,2025)].groupby("year").size().reset_index(name="count")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=yearly["year"], y=yearly["count"],
    mode="lines+markers",
    line=dict(color="#00d4ff", width=3),
    marker=dict(size=8, color="#00d4ff"),
    fill="tozeroy",
    fillcolor="rgba(0,212,255,0.1)",
    name="Reviews"
))
fig.add_vline(x=2020, line_dash="dash", line_color="#ff6b6b", annotation_text="COVID-19")
fig.update_layout(
    template=PLOTLY_TEMPLATE, height=300,
    xaxis_title="Year", yaxis_title="Review Count"
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('<div class="insight-box">📊 Bangkok market fully recovered post-COVID — 2024 hit all-time high with 148,869 reviews. 2025 on track to surpass it.</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#3a4050; font-size:0.75rem; padding:1rem 0;">
    Built by Primesh Marasinghe · Data: Inside Airbnb (Sep 2025) · Expernetic Data Engineer Assessment
</div>
""", unsafe_allow_html=True)