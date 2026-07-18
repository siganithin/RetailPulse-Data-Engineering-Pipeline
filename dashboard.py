"""
RetailPulse
Smart Metadata-Driven Retail Supply Chain Pipeline
Celebal Excellence Internship (CEI) | Final Major Project
Developed by Nithin Siga
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RetailPulse",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PATHS ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database", "retail_pulse.db")

# ── DB HELPER ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data(query: str, params: tuple = ()):
    if not os.path.exists(DB_PATH):
        st.error("Database not found. Run `python main.py` first.")
        st.stop()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)

# ── FILTER BUILDER ───────────────────────────────────────────────────────────
def build_where(region: str, category: str):
    conds, params = [], []
    if region != "All Regions":
        conds.append("s.region = ?")
        params.append(region)
    if category != "All Categories":
        conds.append("p.category = ?")
        params.append(category)
    clause = (" WHERE " + " AND ".join(conds)) if conds else ""
    return clause, tuple(params), list(conds)

# ── PLOTLY CHART THEME ───────────────────────────────────────────────────────
COLORS = ["#1a56db","#e74694","#16bdca","#9061f9","#f59e0b",
          "#10b981","#ef4444","#8b5cf6","#06b6d4","#84cc16"]

def chart_theme(fig, height=380):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(248,250,252,0)",
        paper_bgcolor="rgba(248,250,252,0)",
        font=dict(family="Georgia, 'Times New Roman', serif", color="#1e293b", size=14),
        margin=dict(l=8, r=8, t=36, b=8),
        xaxis=dict(gridcolor="#e2e8f0", linecolor="#cbd5e1",
                   tickfont=dict(color="#475569", size=13)),
        yaxis=dict(gridcolor="#e2e8f0", linecolor="#cbd5e1",
                   tickfont=dict(color="#475569", size=13)),
        legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor="#e2e8f0",
                    borderwidth=1, font=dict(color="#374151", size=13)),
    )
    return fig

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* ─── BASE ─────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
}

.stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #e8edf8 40%, #f4f0ff 70%, #eef4ff 100%);
    min-height: 100vh;
}

[data-testid="stAppViewContainer"] { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }
.block-container { padding: 1.2rem 2rem 3rem 2rem !important; max-width: 1400px; }

/* ─── SCROLLBAR ─────────────────────────────────────────── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-thumb { background:#94a3b8; border-radius:99px; }

/* ─── TOPBAR ────────────────────────────────────────────── */
.topbar {
    background: white;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(30,86,219,0.08);
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-eyebrow {
    font-size: 11px;
    font-weight: 700;
    color: #1a56db;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 4px;
}
.topbar-title {
    font-family: 'EB Garamond', 'Times New Roman', serif !important;
    font-size: 42px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -1px;
    line-height: 1.05;
    margin-bottom: 2px;
}
.topbar-title span { color: #1a56db; }
.topbar-project-title {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    letter-spacing: 0.01em;
    margin-bottom: 10px;
}
.topbar-sub {
    font-size: 14px;
    color: #374151;
    margin-top: 4px;
    font-weight: 400;
    line-height: 1.65;
    max-width: 680px;
}
.topbar-badge {
    display: inline-block;
    background: #eff6ff;
    color: #1a56db;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    padding: 4px 12px;
    margin-right: 6px;
    letter-spacing: 0.03em;
}

/* ─── SECTION DIVIDER ───────────────────────────────────── */
.section-title {
    font-family: 'EB Garamond', 'Times New Roman', serif !important;
    font-size: 24px;
    font-weight: 700;
    color: #0f172a;
    border-left: 4px solid #1a56db;
    padding-left: 12px;
    margin: 20px 0 12px 0;
    line-height: 1.3;
}
.section-sub {
    font-size: 15px;
    color: #64748b;
    margin-bottom: 14px;
    line-height: 1.6;
}

/* ─── METRIC CARDS ──────────────────────────────────────── */
.metric-card {
    background: white;
    border-radius: 14px;
    padding: 22px 20px 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 6px 20px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
    border-top: 4px solid var(--card-color, #1a56db);
    min-height: 160px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    position: relative;
    overflow: hidden;
}
.metric-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.10), 0 12px 28px rgba(26,86,219,0.10);
    transform: translateY(-3px);
}
.metric-icon {
    font-size: 28px;
    margin-bottom: 10px;
    display: block;
}
.metric-label {
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'EB Garamond', 'Times New Roman', serif !important;
    font-size: 32px;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
    margin-bottom: 6px;
}
.metric-caption {
    font-size: 14px;
    color: #64748b;
    line-height: 1.5;
}
.metric-badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 99px;
    margin-top: 10px;
}
.badge-green { background: #d1fae5; color: #065f46; }
.badge-red   { background: #fee2e2; color: #991b1b; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-blue  { background: #dbeafe; color: #1e40af; }

/* ─── FILTER PANEL ──────────────────────────────────────── */
.filter-wrap {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04);
    border: 1px solid #e2e8f0;
}
.filter-heading {
    font-family: 'EB Garamond', 'Times New Roman', serif !important;
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 14px;
}
.filter-label {
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 8px;
}

/* ─── ACTIVE FILTER INDICATOR ───────────────────────────── */
.active-filter-tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1a56db; color: white;
    border-radius: 8px; padding: 5px 14px;
    font-size: 13px; font-weight: 700;
    margin-right: 8px; margin-top: 4px;
}
.filter-neutral-tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f1f5f9; color: #64748b;
    border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 5px 14px;
    font-size: 13px; font-weight: 600;
    margin-right: 8px; margin-top: 4px;
}

/* ─── CHART CARD ────────────────────────────────────────── */
.chart-card {
    background: white;
    border-radius: 14px;
    padding: 20px 18px 12px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 6px 16px rgba(0,0,0,0.04);
    border: 1px solid #e2e8f0;
    margin-bottom: 16px;
}
.chart-title {
    font-family: 'EB Garamond', 'Times New Roman', serif !important;
    font-size: 19px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 3px;
}
.chart-sub {
    font-size: 14px;
    color: #94a3b8;
    margin-bottom: 10px;
}

/* ─── DATA TABLE ────────────────────────────────────────── */
.stDataFrame > div { border-radius: 10px !important; border: 1px solid #e2e8f0 !important; }

/* ─── TABS ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: white !important;
    border-radius: 12px !important;
    padding: 5px 6px !important;
    gap: 2px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07) !important;
    border: 1px solid #e2e8f0 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    padding: 9px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: #1a56db !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(26,86,219,0.3) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ─── BUTTONS ───────────────────────────────────────────── */
.stButton button {
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.18s ease !important;
}
.stButton button[kind="primary"] {
    background: #1a56db !important;
    border: none !important;
    color: white !important;
}
.stButton button[kind="secondary"] {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
}
.stButton button[kind="primary"]:hover { background: #1e40af !important; }

/* ─── INSIGHT STRIP ─────────────────────────────────────── */
.insight-bar {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    border-left: 5px solid #1a56db;
}
.insight-heading {
    font-family: 'EB Garamond', 'Times New Roman', serif !important;
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
}
.insight-text {
    font-size: 15px;
    color: #374151;
    line-height: 1.75;
}
.insight-chip-row { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 14px; }
.insight-chip {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 16px;
    min-width: 180px;
}
.chip-lbl { font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; }
.chip-val { font-family: 'EB Garamond', serif; font-size: 17px; font-weight: 700; color: #0f172a; margin-top: 3px; }

/* ─── SQL TERMINAL ──────────────────────────────────────── */
.stTextArea textarea {
    font-family: 'Courier New', monospace !important;
    font-size: 13px !important;
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #0f172a !important;
}

/* ─── ALERTS ────────────────────────────────────────────── */
.stAlert { border-radius: 10px !important; }

/* ─── SLIDER ────────────────────────────────────────────── */
[data-testid="stSlider"] label {
    font-weight: 600 !important;
    color: #374151 !important;
}

/* ─── SELECTBOX ─────────────────────────────────────────── */
[data-testid="stSelectbox"] label {
    font-weight: 700 !important;
    color: #0f172a !important;
    font-size: 15px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: white !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #0f172a !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stSelectbox"] > div > div:hover {
    border-color: #1a56db !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.12) !important;
}

/* Active selectbox — when value is not default, highlight border */
.active-select > div > div {
    border-color: #1a56db !important;
    background: #eff6ff !important;
    color: #1a56db !important;
}

hr { border-color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── TOP NAVIGATION BAR ───────────────────────────────────────────────────────
total_rev_all = load_data("SELECT ROUND(SUM(total_amount),2) as r FROM orders")["r"].iloc[0] or 0
total_ord_all = load_data("SELECT COUNT(DISTINCT order_id) as c FROM orders")["c"].iloc[0] or 0
total_sku_all = load_data("SELECT COUNT(*) as c FROM products")["c"].iloc[0] or 0
total_stores  = load_data("SELECT COUNT(*) as c FROM stores")["c"].iloc[0] or 0

st.markdown(f"""
<div class="topbar">
  <div>
    <div class="topbar-title"><span>RetailPulse</span></div>
    <div class="topbar-project-title">Smart Metadata-Driven Retail Supply Chain Pipeline</div>
    <div class="topbar-sub">
      RetailPulse is an end-to-end retail data engineering application implementing the
      Medallion Architecture (Bronze&nbsp;→&nbsp;Silver&nbsp;→&nbsp;Gold). It transforms
      fragmented retail operational data into analytics-ready datasets and business insights
      using Python, Pandas, SQLite, Streamlit, and Databricks&nbsp;(PySpark).
    </div>
    <div style="margin-top:12px">
      <span class="topbar-badge">Python + Pandas</span>
      <span class="topbar-badge">SQLite Analytics</span>
      <span class="topbar-badge">Bronze → Silver → Gold</span>
      <span class="topbar-badge">Streamlit</span>
      <span class="topbar-badge">Databricks · PySpark</span>
    </div>
  </div>
  <div style="display:flex; gap:20px; flex-shrink:0;">
    <div style="text-align:center; padding:0 16px; border-left:1px solid #e2e8f0;">
      <div style="font-size:12px; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:.07em;">Total Revenue</div>
      <div style="font-family:'EB Garamond',serif; font-size:26px; font-weight:700; color:#0f172a; margin-top:4px;">₹{total_rev_all/100000:.1f}L</div>
    </div>
    <div style="text-align:center; padding:0 16px; border-left:1px solid #e2e8f0;">
      <div style="font-size:12px; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:.07em;">Orders</div>
      <div style="font-family:'EB Garamond',serif; font-size:26px; font-weight:700; color:#0f172a; margin-top:4px;">{total_ord_all:,}</div>
    </div>
    <div style="text-align:center; padding:0 16px; border-left:1px solid #e2e8f0;">
      <div style="font-size:12px; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:.07em;">SKUs</div>
      <div style="font-family:'EB Garamond',serif; font-size:26px; font-weight:700; color:#0f172a; margin-top:4px;">{total_sku_all}</div>
    </div>
    <div style="text-align:center; padding:0 16px; border-left:1px solid #e2e8f0;">
      <div style="font-size:12px; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:.07em;">Stores</div>
      <div style="font-family:'EB Garamond',serif; font-size:26px; font-weight:700; color:#0f172a; margin-top:4px;">{total_stores}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FILTER PANEL ─────────────────────────────────────────────────────────────
regions    = ["All Regions"]    + sorted(load_data("SELECT DISTINCT region FROM stores")["region"].tolist())
categories = ["All Categories"] + sorted(load_data("SELECT DISTINCT category FROM products")["category"].tolist())

st.markdown('<div class="filter-wrap"><div class="filter-heading">🔍 Filter Controls</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns([1, 1, 2])
with f1:
    selected_region = st.selectbox(
        "📍 Region",
        regions,
        index=regions.index(st.session_state.get("sel_region", "All Regions")),
        key="sel_region",
        help="Filter all metrics and charts by region",
    )
with f2:
    selected_category = st.selectbox(
        "📦 Product Category",
        categories,
        index=categories.index(st.session_state.get("sel_category", "All Categories")),
        key="sel_category",
        help="Filter all metrics and charts by product category",
    )
with f3:
    # Show active filter summary tags
    region_is_filtered   = selected_region   != "All Regions"
    category_is_filtered = selected_category != "All Categories"

    active_html = '<div style="padding-top:28px; display:flex; flex-wrap:wrap; gap:8px; align-items:center;">'
    active_html += '<span style="font-size:13px; font-weight:600; color:#64748b;">Active filters:</span>'

    if region_is_filtered:
        active_html += f'<span class="active-filter-tag">📍 {selected_region} ✕</span>'
    else:
        active_html += '<span class="filter-neutral-tag">📍 All Regions</span>'

    if category_is_filtered:
        active_html += f'<span class="active-filter-tag">📦 {selected_category} ✕</span>'
    else:
        active_html += '<span class="filter-neutral-tag">📦 All Categories</span>'

    if region_is_filtered or category_is_filtered:
        active_html += '<span style="font-size:13px; color:#1a56db; font-weight:700; margin-left:4px;">● Filtered View</span>'
    else:
        active_html += '<span style="font-size:13px; color:#94a3b8; font-weight:600; margin-left:4px;">Showing all data</span>'

    active_html += '</div>'
    st.markdown(active_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

where_clause, params, conds = build_where(selected_region, selected_category)

# ── KPI CALCULATIONS ─────────────────────────────────────────────────────────
df_orders = load_data(f"""
    SELECT o.total_amount, o.quantity, o.order_id
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    JOIN stores   s ON o.store_id   = s.store_id
    {where_clause}
""", params)

total_revenue = float(df_orders["total_amount"].sum())
total_orders  = int(df_orders["order_id"].nunique())
avg_order_val = float(df_orders["total_amount"].mean()) if total_orders > 0 else 0.0
total_units   = int(df_orders["quantity"].sum())

ls_conds = conds + ["i.stock_level < i.reorder_level"]
ls_where  = " WHERE " + " AND ".join(ls_conds)
low_stock_count = int(load_data(f"""
    SELECT COUNT(*) as cnt FROM inventory i
    JOIN products p ON i.product_id = p.product_id
    JOIN stores   s ON i.store_id   = s.store_id
    {ls_where}
""", params)["cnt"].iloc[0])

# ── METRIC CARDS ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Live metrics for the selected region and product category filter.</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card" style="--card-color:#1a56db">
      <span class="metric-icon">💰</span>
      <div class="metric-label">Gross Revenue</div>
      <div class="metric-value">₹{total_revenue:,.0f}</div>
      <div class="metric-caption">Total sales value for selected business lens</div>
      <span class="metric-badge badge-blue">▲ Revenue On Track</span>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card" style="--card-color:#f59e0b">
      <span class="metric-icon">🛒</span>
      <div class="metric-label">Order Volume</div>
      <div class="metric-value">{total_orders:,}</div>
      <div class="metric-caption">Fulfilled order transactions in current view</div>
      <span class="metric-badge badge-green">● Healthy Velocity</span>
    </div>""", unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card" style="--card-color:#10b981">
      <span class="metric-icon">🧾</span>
      <div class="metric-label">Avg. Ticket Value</div>
      <div class="metric-value">₹{avg_order_val:,.0f}</div>
      <div class="metric-caption">Average basket size across active segment</div>
      <span class="metric-badge badge-green">● Optimised AOV</span>
    </div>""", unsafe_allow_html=True)

with m4:
    badge_cls  = "badge-red"   if low_stock_count > 0 else "badge-green"
    badge_text = "⚠ Action Required" if low_stock_count > 0 else "● Fully Stocked"
    card_color = "#ef4444" if low_stock_count > 0 else "#10b981"
    st.markdown(f"""
    <div class="metric-card" style="--card-color:{card_color}">
      <span class="metric-icon">{'⚠️' if low_stock_count > 0 else '✅'}</span>
      <div class="metric-label">Stockout Alerts</div>
      <div class="metric-value">{low_stock_count}</div>
      <div class="metric-caption">Items sitting below safety reorder thresholds</div>
      <span class="metric-badge {badge_cls}">{badge_text}</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── INTELLIGENCE SUMMARY BAR ─────────────────────────────────────────────────
top_store = load_data(f"""
    SELECT s.store_name, ROUND(SUM(o.total_amount),2) as rev
    FROM orders o JOIN stores s ON o.store_id=s.store_id
    JOIN products p ON o.product_id=p.product_id {where_clause}
    GROUP BY s.store_name ORDER BY rev DESC LIMIT 1""", params)

top_cat = load_data(f"""
    SELECT p.category, ROUND(SUM(o.total_amount),2) as rev
    FROM orders o JOIN products p ON o.product_id=p.product_id
    JOIN stores s ON o.store_id=s.store_id {where_clause}
    GROUP BY p.category ORDER BY rev DESC LIMIT 1""", params)

urgent_where = (f"{where_clause} AND i.stock_level < i.reorder_level"
                if where_clause else "WHERE i.stock_level < i.reorder_level")
urgent_item = load_data(f"""
    SELECT p.product_name, (i.reorder_level - i.stock_level) as deficit
    FROM inventory i JOIN products p ON i.product_id=p.product_id
    JOIN stores s ON i.store_id=s.store_id {urgent_where}
    ORDER BY deficit DESC LIMIT 1""", params)

top_store_name = top_store["store_name"].iloc[0]  if not top_store.empty  else "—"
top_cat_name   = top_cat["category"].iloc[0]       if not top_cat.empty    else "—"
urgent_name    = urgent_item["product_name"].iloc[0] if not urgent_item.empty else "All Clear"

insight_text = (
    f"Viewing <strong>{selected_region}</strong> · <strong>{selected_category}</strong>. "
    f"This lens covers <strong>{total_orders:,} orders</strong> worth "
    f"<strong>₹{total_revenue:,.0f}</strong> in gross revenue "
    f"with <strong>{total_units:,} units dispatched</strong>. "
    f"<strong>{low_stock_count} items</strong> are currently below reorder safety thresholds — "
    + ("immediate replenishment is advised." if low_stock_count > 0 else "inventory levels are healthy.")
)

st.markdown(f"""
<div class="insight-bar">
  <div class="insight-heading">📊 Live Intelligence Summary</div>
  <div class="insight-text">{insight_text}</div>
  <div class="insight-chip-row">
    <div class="insight-chip">
      <div class="chip-lbl">🏆 Top Performing Store</div>
      <div class="chip-val">{top_store_name}</div>
    </div>
    <div class="insight-chip">
      <div class="chip-lbl">📦 Leading Category</div>
      <div class="chip-val">{top_cat_name}</div>
    </div>
    <div class="insight-chip">
      <div class="chip-lbl">🚨 Urgent Replenishment</div>
      <div class="chip-val">{urgent_name}</div>
    </div>
    <div class="insight-chip">
      <div class="chip-lbl">📦 Units Dispatched</div>
      <div class="chip-val">{total_units:,}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
#  NAVIGATION TABS
# ════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📈  Sales Engine",
    "🏆  Top Products",
    "🚨  Stockout Alerts",
    "🎮  Demand Simulator",
    "💻  SQL Explorer",
    "☁️  Enterprise Scalability",
    "📝  Engineering Journey",
])

# ──────────────────────────────────────────────────────────────────────
# TAB 0 — SALES ENGINE
# ──────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="section-title">📈 Core Sales Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Daily revenue trends, store leaderboard, and category contribution — filtered to your active lens.</div>', unsafe_allow_html=True)

    # Daily revenue
    daily_q = load_data(f"""
        SELECT o.order_date as date, ROUND(SUM(o.total_amount),2) as revenue
        FROM orders o JOIN products p ON o.product_id=p.product_id
        JOIN stores s ON o.store_id=s.store_id {where_clause}
        GROUP BY o.order_date ORDER BY o.order_date""", params)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="chart-card"><div class="chart-title">Daily Revenue Trend</div><div class="chart-sub">Total sales value per day with 7-day rolling average overlay</div>', unsafe_allow_html=True)
        if not daily_q.empty:
            daily_q["date"] = pd.to_datetime(daily_q["date"])
            daily_q["rolling7"] = daily_q["revenue"].rolling(7, min_periods=1).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_q["date"], y=daily_q["revenue"],
                name="Daily Revenue", mode="lines",
                line=dict(color="#1a56db", width=1.8),
                fill="tozeroy", fillcolor="rgba(26,86,219,0.07)",
            ))
            fig.add_trace(go.Scatter(
                x=daily_q["date"], y=daily_q["rolling7"],
                name="7-Day Avg", mode="lines",
                line=dict(color="#e74694", width=2, dash="dot"),
            ))
            fig.update_layout(xaxis_title="Date", yaxis_title="Revenue (₹)", hovermode="x unified")
            chart_theme(fig, 340)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for current filter.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="chart-card"><div class="chart-title">Store Revenue Leaderboard</div><div class="chart-sub">Ranked branch-level sales performance</div>', unsafe_allow_html=True)
        store_q = load_data(f"""
            SELECT s.store_name, ROUND(SUM(o.total_amount),2) as revenue
            FROM orders o JOIN stores s ON o.store_id=s.store_id
            JOIN products p ON o.product_id=p.product_id {where_clause}
            GROUP BY s.store_name ORDER BY revenue DESC""", params)
        if not store_q.empty:
            store_q["label"] = store_q["store_name"].str.replace("RetailPulse ", "", regex=False)
            fig2 = go.Figure(go.Bar(
                x=store_q["revenue"], y=store_q["label"],
                orientation="h",
                marker=dict(
                    color=list(range(len(store_q))),
                    colorscale=[[0, "#93c5fd"], [1, "#1a56db"]],
                    showscale=False,
                    line=dict(width=0),
                ),
                text=[f"₹{v/1000:.0f}k" for v in store_q["revenue"]],
                textposition="outside",
                textfont=dict(color="#374151", size=11),
            ))
            fig2.update_layout(xaxis_title="Revenue (₹)", yaxis=dict(autorange="reversed"))
            chart_theme(fig2, 340)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No store data.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Category breakdown
    st.markdown('<div class="section-title" style="font-size:18px">📦 Category Revenue Breakdown</div>', unsafe_allow_html=True)
    cat_q = load_data(f"""
        SELECT p.category, SUM(o.quantity) as units, ROUND(SUM(o.total_amount),2) as revenue
        FROM orders o JOIN products p ON o.product_id=p.product_id
        JOIN stores s ON o.store_id=s.store_id {where_clause}
        GROUP BY p.category ORDER BY revenue DESC""", params)

    pc1, pc2 = st.columns([2, 3])
    with pc1:
        if not cat_q.empty:
            fig3 = px.bar(cat_q, x="revenue", y="category", orientation="h",
                          color="category", color_discrete_sequence=COLORS,
                          labels={"revenue": "Revenue (₹)", "category": "Category"})
            fig3.update_traces(showlegend=False)
            fig3.update_layout(yaxis=dict(autorange="reversed"))
            chart_theme(fig3, 340)
            st.plotly_chart(fig3, use_container_width=True)
    with pc2:
        if not cat_q.empty:
            cat_q.columns = ["Category", "Units Dispatched", "Gross Revenue (₹)"]
            st.dataframe(cat_q, use_container_width=True, hide_index=True, height=340)

# ──────────────────────────────────────────────────────────────────────
# TAB 1 — TOP PRODUCTS
# ──────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="section-title">🏆 Top Products Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Revenue leaders and volume analysis across the active filter lens. Identifies best-selling SKUs for strategic inventory planning.</div>', unsafe_allow_html=True)

    top_prod = load_data(f"""
        SELECT p.product_name, p.category,
               ROUND(SUM(o.total_amount),2) as revenue,
               SUM(o.quantity) as units
        FROM orders o JOIN products p ON o.product_id=p.product_id
        JOIN stores s ON o.store_id=s.store_id {where_clause}
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY revenue DESC LIMIT 10""", params)

    tp1, tp2 = st.columns([3, 2])
    with tp1:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Products by Revenue</div><div class="chart-sub">Horizontal bar — highest revenue generators in selected lens</div>', unsafe_allow_html=True)
        if not top_prod.empty:
            fig_tp = go.Figure(go.Bar(
                y=top_prod["product_name"], x=top_prod["revenue"],
                orientation="h",
                marker=dict(
                    color=list(range(len(top_prod))),
                    colorscale=[[0,"#bfdbfe"],[1,"#1a56db"]],
                    showscale=False, line=dict(width=0),
                ),
                text=[f"₹{v:,.0f}" for v in top_prod["revenue"]],
                textposition="outside",
                textfont=dict(color="#374151", size=11),
            ))
            fig_tp.update_layout(xaxis_title="Revenue (₹)",
                                 yaxis=dict(autorange="reversed"))
            chart_theme(fig_tp, 420)
            st.plotly_chart(fig_tp, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tp2:
        st.markdown('<div class="chart-card"><div class="chart-title">Volume vs Revenue</div><div class="chart-sub">Scatter — does high unit volume always mean high revenue?</div>', unsafe_allow_html=True)
        if not top_prod.empty:
            fig_sc = px.scatter(
                top_prod, x="units", y="revenue",
                color="category", size="revenue",
                text="product_name",
                color_discrete_sequence=COLORS,
                labels={"units": "Units Sold", "revenue": "Revenue (₹)"},
            )
            fig_sc.update_traces(
                textposition="top center",
                textfont=dict(size=9, color="#374151"),
                marker=dict(line=dict(width=0)),
            )
            chart_theme(fig_sc, 420)
            st.plotly_chart(fig_sc, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title" style="font-size:18px">📋 Full Product Revenue Table</div>', unsafe_allow_html=True)
    if not top_prod.empty:
        display = top_prod.copy()
        display.columns = ["Product Name", "Category", "Total Revenue (₹)", "Units Sold"]
        st.dataframe(display, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────
# TAB 2 — STOCKOUT ALERTS
# ──────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="section-title">🚨 Supply Chain Bottleneck Diagnostic</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Products currently below their reorder safety levels, ranked by replenishment urgency. Red rows indicate zero-stock (active stockout). Amber rows indicate critically low levels (≤ 5 units).</div>', unsafe_allow_html=True)

    alert_conds = conds + ["i.stock_level < i.reorder_level"]
    alert_where = " WHERE " + " AND ".join(alert_conds)

    df_alerts = load_data(f"""
        SELECT p.product_name        AS "Product Name",
               s.store_name          AS "Store",
               p.category            AS "Category",
               i.stock_level         AS "Current Stock",
               i.reorder_level       AS "Reorder Level",
               (i.reorder_level - i.stock_level) AS "Deficit",
               sup.supplier_name     AS "Supplier",
               sup.lead_time_days    AS "Lead Days",
               sup.rating            AS "Supplier Rating"
        FROM inventory i
        JOIN products  p   ON i.product_id  = p.product_id
        JOIN stores    s   ON i.store_id    = s.store_id
        JOIN suppliers sup ON p.supplier_id = sup.supplier_id
        {alert_where}
        ORDER BY "Deficit" DESC""", params)

    if df_alerts.empty:
        st.success("✅ All products are stocked above their safety reorder levels for this selection.")
    else:
        total_deficit  = int(df_alerts["Deficit"].sum())
        critical_count = int((df_alerts["Current Stock"] == 0).sum())

        sa1, sa2, sa3 = st.columns(3)
        sa1.metric("🚨 Alert Lines",        str(len(df_alerts)))
        sa2.metric("🛑 Zero-Stock Items",   str(critical_count))
        sa3.metric("📦 Total Units Needed", f"{total_deficit:,}")
        st.markdown("<br>", unsafe_allow_html=True)

        # Chart — top 15 deficit items
        top15 = df_alerts.head(15).copy()
        st.markdown('<div class="chart-card"><div class="chart-title">Top 15 Replenishment Deficits</div><div class="chart-sub">Items with the largest gap between current stock and reorder threshold</div>', unsafe_allow_html=True)
        fig_al = go.Figure(go.Bar(
            x=top15["Deficit"],
            y=top15["Product Name"] + " @ " + top15["Store"].str.replace("RetailPulse ", "", regex=False),
            orientation="h",
            marker=dict(
                color=top15["Deficit"],
                colorscale=[[0,"#fbbf24"],[0.5,"#f97316"],[1,"#ef4444"]],
                showscale=False, line=dict(width=0),
            ),
            text=top15["Deficit"].astype(str) + " units",
            textposition="outside",
            textfont=dict(color="#374151", size=11),
        ))
        fig_al.update_layout(
            xaxis_title="Units Needed to Reach Reorder Level",
            yaxis=dict(autorange="reversed"),
        )
        chart_theme(fig_al, 480)
        st.plotly_chart(fig_al, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:18px">📋 Full Stockout Alert Table</div>', unsafe_allow_html=True)

        def color_rows(row):
            if row["Current Stock"] == 0:
                return ["background-color:#fee2e2; color:#7f1d1d; font-weight:600"] * len(row)
            elif row["Current Stock"] <= 5:
                return ["background-color:#fef3c7; color:#78350f"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_alerts.style.apply(color_rows, axis=1),
            use_container_width=True,
            hide_index=True,
        )

# ──────────────────────────────────────────────────────────────────────
# TAB 3 — DEMAND SPIKE SIMULATOR
# ──────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-title">🎮 Demand Spike Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Models the impact of a sudden demand surge — such as a festival sale or flash event — on current inventory levels. Projects which products will hit stockout within 7 days under the simulated scenario.</div>', unsafe_allow_html=True)

    sim_c1, sim_c2 = st.columns([1, 2])
    with sim_c1:
        sim_spike = st.slider("Demand Spike (%)", 10, 150, 30, 10,
                              help="Percentage increase above the baseline daily demand rate.")
        store_opts = ["All Stores"] + load_data(
            "SELECT DISTINCT store_name FROM stores ORDER BY store_name"
        )["store_name"].tolist()
        sim_store = st.selectbox("Filter by Store", store_opts)

    with sim_c2:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #10b981;
             border-radius:12px; padding:18px 20px; font-size:14px; color:#374151; line-height:1.8;">
          <strong style="font-family:'EB Garamond',serif; font-size:16px; color:#0f172a">
            How the Simulation Works
          </strong><br>
          The simulator computes the <strong>average daily sales velocity</strong> for each
          product-store pair (total units sold ÷ 90 days). It then applies a
          <strong>+{sim_spike}%</strong> demand multiplier, projects cumulative consumption
          over <strong>7 days</strong>, and flags any item whose projected remaining stock
          falls below zero — indicating a real-world stockout risk before the next
          replenishment cycle arrives.
        </div>""", unsafe_allow_html=True)

    # Simulation computation
    df_vel = load_data("""
        SELECT o.store_id, s.store_name, o.product_id, p.product_name, p.category,
               SUM(o.quantity) as total_sold
        FROM orders o JOIN products p ON o.product_id=p.product_id
        JOIN stores s ON o.store_id=s.store_id
        GROUP BY o.store_id, o.product_id""")

    df_inv_sim = load_data("SELECT store_id, product_id, stock_level, reorder_level FROM inventory")
    df_sim = pd.merge(df_vel, df_inv_sim, on=["store_id", "product_id"])
    df_sim["avg_daily"]  = df_sim["total_sold"] / 90.0
    multiplier           = 1 + (sim_spike / 100.0)
    df_sim["demand_7d"]  = (df_sim["avg_daily"] * 7 * multiplier).round(1)
    df_sim["proj_stock"] = (df_sim["stock_level"] - df_sim["demand_7d"]).round(1)

    if sim_store != "All Stores":
        df_sim = df_sim[df_sim["store_name"] == sim_store]

    df_runout = df_sim[df_sim["proj_stock"] < 0].copy()
    df_runout["Estimated Deficit"] = (-df_runout["proj_stock"]).astype(int)
    df_runout = df_runout.sort_values("Estimated Deficit", ascending=False)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title" style="font-size:18px">🔮 7-Day Projected Stockouts — +{sim_spike}% Demand Scenario</div>', unsafe_allow_html=True)

    if df_runout.empty:
        st.success(f"✅ All products can sustain a +{sim_spike}% demand spike for the next 7 days without any stockouts.")
    else:
        ss1, ss2, ss3 = st.columns(3)
        ss1.metric("Products at Risk",      str(len(df_runout)))
        ss2.metric("Units to Pre-Order",    f"{df_runout['Estimated Deficit'].sum():,}")
        ss3.metric("Stores Impacted",       str(df_runout["store_name"].nunique()))
        st.markdown("<br>", unsafe_allow_html=True)

        top_sim = df_runout.head(15)
        st.markdown('<div class="chart-card"><div class="chart-title">Top 15 Projected Stockouts</div><div class="chart-sub">Estimated deficit per product-store pair under the demand spike scenario</div>', unsafe_allow_html=True)
        fig_sim = go.Figure(go.Bar(
            x=top_sim["Estimated Deficit"],
            y=top_sim["product_name"] + " · " + top_sim["store_name"].str.replace("RetailPulse ", "", regex=False),
            orientation="h",
            marker=dict(
                color=top_sim["Estimated Deficit"],
                colorscale=[[0,"#a5f3fc"],[0.5,"#f59e0b"],[1,"#dc2626"]],
                showscale=False, line=dict(width=0),
            ),
            text=top_sim["Estimated Deficit"].astype(str) + " units",
            textposition="outside",
            textfont=dict(color="#374151", size=11),
        ))
        fig_sim.update_layout(
            xaxis_title="Estimated Deficit (Units)",
            yaxis=dict(autorange="reversed"),
        )
        chart_theme(fig_sim, 460)
        st.plotly_chart(fig_sim, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        rename_map = {
            "product_name": "Product", "store_name": "Store",
            "category": "Category",   "stock_level": "Current Stock",
            "demand_7d": "Projected Demand (7d)",
            "proj_stock": "Projected Remaining Stock",
        }
        show_cols = ["product_name","store_name","category",
                     "stock_level","demand_7d","proj_stock","Estimated Deficit"]
        st.dataframe(
            df_runout[show_cols].rename(columns=rename_map),
            use_container_width=True, hide_index=True,
        )
        st.warning(
            f"⚠️ Under a **+{sim_spike}%** demand surge, **{len(df_runout)} product lines** "
            f"across **{df_runout['store_name'].nunique()} stores** will face stockouts "
            f"within the week. Pre-order the 'Estimated Deficit' quantities immediately."
        )

# ──────────────────────────────────────────────────────────────────────
# TAB 4 — SQL EXPLORER
# ──────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown('<div class="section-title">💻 SQLite Interactive Query Terminal</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Write and execute raw SQL directly against the <code>retail_pulse.db</code> database. Inspect schemas, run custom aggregations, and explore the data layer directly.</div>', unsafe_allow_html=True)

    SAMPLE_QUERIES = {
        "Products Preview":
            "SELECT * FROM products LIMIT 10;",
        "Revenue by Category":
            "SELECT p.category,\n       ROUND(SUM(o.total_amount),2) AS total_revenue,\n       SUM(o.quantity) AS total_units\nFROM orders o\nJOIN products p ON o.product_id = p.product_id\nGROUP BY p.category\nORDER BY total_revenue DESC;",
        "Supplier Performance":
            "SELECT supplier_name, rating, lead_time_days, contact_city\nFROM suppliers\nORDER BY rating DESC;",
        "Store Sales Ranking":
            "SELECT s.store_name, s.city, s.region,\n       ROUND(SUM(o.total_amount),2) AS revenue,\n       COUNT(o.order_id) AS orders\nFROM orders o\nJOIN stores s ON o.store_id = s.store_id\nGROUP BY s.store_name\nORDER BY revenue DESC;",
        "Low Stock Report":
            "SELECT p.product_name, s.store_name,\n       i.stock_level, i.reorder_level,\n       (i.reorder_level - i.stock_level) AS deficit\nFROM inventory i\nJOIN products p ON i.product_id = p.product_id\nJOIN stores   s ON i.store_id   = s.store_id\nWHERE i.stock_level < i.reorder_level\nORDER BY deficit DESC\nLIMIT 20;",
    }

    sq1, sq2 = st.columns([3, 2])
    with sq1:
        if "sql_text" not in st.session_state:
            st.session_state["sql_text"] = list(SAMPLE_QUERIES.values())[0]

        st.markdown('<div class="filter-label">Quick Templates</div>', unsafe_allow_html=True)
        btn_row = st.columns(len(SAMPLE_QUERIES))
        for i, (label, qry) in enumerate(SAMPLE_QUERIES.items()):
            if btn_row[i].button(label, key=f"sqt_{i}", use_container_width=True):
                st.session_state["sql_text"] = qry

        user_sql = st.text_area(
            "SQL Query Editor",
            value=st.session_state["sql_text"],
            height=180,
            key="sql_editor",
        )

        if st.button("▶  Execute Query", type="primary"):
            if not user_sql.strip():
                st.warning("Please enter a SQL query first.")
            else:
                try:
                    result_df = load_data(user_sql)
                    st.success(f"Query executed successfully — {len(result_df)} rows returned.")
                    st.dataframe(result_df, use_container_width=True)
                except Exception as exc:
                    st.error(f"SQL Error: {exc}")

    with sq2:
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:20px 22px; font-size:13px; line-height:1.85;">
          <div style="font-family:'EB Garamond',serif; font-size:17px; font-weight:700;
               color:#0f172a; margin-bottom:12px;">📋 Database Schema</div>

          <div style="font-weight:700; color:#1a56db; margin-bottom:3px">orders</div>
          <div style="color:#6b7280; font-family:'Courier New',monospace; margin-bottom:10px; padding-left:8px">
            order_id · product_id · store_id<br>
            quantity · price · order_date · total_amount</div>

          <div style="font-weight:700; color:#1a56db; margin-bottom:3px">inventory</div>
          <div style="color:#6b7280; font-family:'Courier New',monospace; margin-bottom:10px; padding-left:8px">
            product_id · store_id · stock_level<br>
            reorder_level · last_updated · low_stock_flag</div>

          <div style="font-weight:700; color:#1a56db; margin-bottom:3px">products</div>
          <div style="color:#6b7280; font-family:'Courier New',monospace; margin-bottom:10px; padding-left:8px">
            product_id · product_name · category · supplier_id</div>

          <div style="font-weight:700; color:#1a56db; margin-bottom:3px">stores</div>
          <div style="color:#6b7280; font-family:'Courier New',monospace; margin-bottom:10px; padding-left:8px">
            store_id · store_name · city · region</div>

          <div style="font-weight:700; color:#1a56db; margin-bottom:3px">suppliers</div>
          <div style="color:#6b7280; font-family:'Courier New',monospace; padding-left:8px">
            supplier_id · supplier_name · contact_city<br>
            lead_time_days · rating</div>
        </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# TAB 5 — ENTERPRISE SCALABILITY WITH DATABRICKS
# ──────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown('<div class="section-title">☁️ Enterprise Scalability with Databricks</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-sub">
      RetailPulse is fully functional on a local machine using Python, Pandas, SQLite, and Streamlit.
      To demonstrate enterprise readiness, the same Medallion Architecture has also been implemented
      in Databricks using PySpark and Delta Lake. This enables the pipeline to process significantly
      larger datasets while preserving the same Bronze → Silver → Gold workflow.
    </div>""", unsafe_allow_html=True)

    # ── Row 1: Why Databricks + Local vs Enterprise ──────────────────
    db_r1c1, db_r1c2 = st.columns(2)

    with db_r1c1:
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; margin-bottom:16px; border-top:4px solid #1a56db; height:100%;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:14px;">Why Databricks?</div>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:0;">
            RetailPulse was initially developed as a local data engineering project for ease of
            development and demonstration. While this approach is ideal for moderate datasets,
            enterprise retail organisations generate millions of transactions every day that
            require distributed processing.<br><br>
            To address this scalability requirement, an equivalent implementation of the pipeline
            was developed in Databricks.<br><br>
            The Databricks version replaces:
          </p>
          <ul style="font-size:15px; color:#374151; line-height:2.1; margin:14px 0 0 0; padding-left:18px;">
            <li><strong>Pandas</strong> with Apache Spark (PySpark)</li>
            <li><strong>CSV processing</strong> with Delta Lake tables</li>
            <li><strong>SQLite SQL</strong> with Spark SQL</li>
            <li><strong>Single-machine execution</strong> with distributed computing</li>
          </ul>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:14px 0 0 0;">
            The overall business logic remains unchanged, ensuring consistency between
            local and cloud implementations.
          </p>
        </div>""", unsafe_allow_html=True)

    with db_r1c2:
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; margin-bottom:16px; border-top:4px solid #9061f9; height:100%;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:16px;">Local vs Enterprise Implementation</div>
          <table style="width:100%; border-collapse:collapse; font-size:15px;">
            <thead>
              <tr style="background:#f0f4ff; border-radius:8px;">
                <th style="padding:11px 14px; text-align:left; color:#1a56db; font-weight:700;
                    border-bottom:2px solid #e2e8f0;">Local Implementation</th>
                <th style="padding:11px 14px; text-align:left; color:#7c3aed; font-weight:700;
                    border-bottom:2px solid #e2e8f0;">Enterprise Implementation</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding:10px 14px; color:#374151;">Python</td>
                <td style="padding:10px 14px; color:#374151; font-weight:600;">PySpark</td>
              </tr>
              <tr style="border-bottom:1px solid #f1f5f9; background:#fafafa;">
                <td style="padding:10px 14px; color:#374151;">Pandas</td>
                <td style="padding:10px 14px; color:#374151; font-weight:600;">Spark DataFrames</td>
              </tr>
              <tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding:10px 14px; color:#374151;">CSV Files</td>
                <td style="padding:10px 14px; color:#374151; font-weight:600;">Delta Lake</td>
              </tr>
              <tr style="border-bottom:1px solid #f1f5f9; background:#fafafa;">
                <td style="padding:10px 14px; color:#374151;">SQLite</td>
                <td style="padding:10px 14px; color:#374151; font-weight:600;">Spark SQL</td>
              </tr>
              <tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding:10px 14px; color:#374151;">Streamlit Dashboard</td>
                <td style="padding:10px 14px; color:#374151; font-weight:600;">BI Tools / Dashboards</td>
              </tr>
              <tr style="background:#fafafa;">
                <td style="padding:10px 14px; color:#374151;">Single Machine</td>
                <td style="padding:10px 14px; color:#374151; font-weight:600;">Distributed Cluster</td>
              </tr>
            </tbody>
          </table>
        </div>""", unsafe_allow_html=True)

    # ── Row 2: Enterprise Pipeline + Benefits ────────────────────────
    db_r2c1, db_r2c2 = st.columns(2)

    with db_r2c1:
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; margin-bottom:16px; border-top:4px solid #10b981;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:16px;">Enterprise Pipeline Architecture</div>
          <div style="display:flex; gap:16px;">
            <div style="flex:1; background:#f0f7ff; border-radius:10px; padding:16px 18px;
                 border:1px solid #bfdbfe;">
              <div style="font-size:13px; font-weight:700; color:#1a56db; text-transform:uppercase;
                   letter-spacing:.06em; margin-bottom:10px;">LOCAL</div>
              <div style="font-size:14px; color:#374151; line-height:2.3;">
                Raw CSV<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                Bronze<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                Silver<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                Gold<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                SQLite<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                <strong>Streamlit Dashboard</strong>
              </div>
            </div>
            <div style="flex:1; background:#f5f0ff; border-radius:10px; padding:16px 18px;
                 border:1px solid #ddd6fe;">
              <div style="font-size:13px; font-weight:700; color:#7c3aed; text-transform:uppercase;
                   letter-spacing:.06em; margin-bottom:10px;">DATABRICKS</div>
              <div style="font-size:14px; color:#374151; line-height:2.3;">
                Raw CSV<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                Bronze Delta<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                Silver Delta<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                Gold Delta<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                Spark SQL<br>
                <span style="color:#94a3b8; font-size:13px;">↓</span><br>
                <strong>Power BI / Tableau</strong>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    with db_r2c2:
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; margin-bottom:16px; border-top:4px solid #f59e0b;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:16px;">Benefits of Databricks</div>
          <div style="display:flex; flex-direction:column; gap:12px; font-size:15px; color:#374151;">
            <div style="background:#f8fafc; border-radius:10px; padding:12px 16px;
                 border-left:3px solid #1a56db;">
              <strong style="color:#0f172a;">Distributed Processing</strong><br>
              <span style="color:#64748b; font-size:14px;">Multiple worker nodes process data in parallel,
              enabling significantly faster execution on large datasets.</span>
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:12px 16px;
                 border-left:3px solid #9061f9;">
              <strong style="color:#0f172a;">Delta Lake</strong><br>
              <span style="color:#64748b; font-size:14px;">Provides ACID transactions, schema enforcement,
              version history, and reliable data management.</span>
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:12px 16px;
                 border-left:3px solid #10b981;">
              <strong style="color:#0f172a;">Spark SQL</strong><br>
              <span style="color:#64748b; font-size:14px;">Supports distributed SQL queries while
              maintaining syntax similar to standard SQL.</span>
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:12px 16px;
                 border-left:3px solid #f59e0b;">
              <strong style="color:#0f172a;">Scalability</strong><br>
              <span style="color:#64748b; font-size:14px;">Same pipeline scales from thousands to
              millions of records without redesigning the architecture.</span>
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:12px 16px;
                 border-left:3px solid #ef4444;">
              <strong style="color:#0f172a;">Production Ready</strong><br>
              <span style="color:#64748b; font-size:14px;">Supports workflow scheduling, cloud storage
              integration, and enterprise deployment.</span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Row 3: Implementation in this project (full width) ───────────
    st.markdown("""
    <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
         padding:26px; border-top:4px solid #16bdca;">
      <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
           color:#0f172a; margin-bottom:14px;">Databricks Implementation in this Project</div>
      <p style="font-size:15px; color:#374151; line-height:1.85; margin:0 0 14px 0;">
        RetailPulse includes a complete PySpark implementation of the Medallion Architecture
        in <code>notebooks/retail_pulse_databricks.py</code>.
        The notebook reproduces each stage of the local pipeline:
      </p>
      <div style="display:flex; gap:16px; flex-wrap:wrap;">
        <div style="flex:1; min-width:200px; background:#f0f7ff; border-radius:10px;
             padding:16px 18px; border:1px solid #bfdbfe;">
          <div style="font-size:13px; font-weight:700; color:#1a56db; margin-bottom:6px;">
            BRONZE LAYER
          </div>
          <div style="font-size:14px; color:#374151;">
            Raw data ingested from DBFS into Delta tables — no transformation applied.
          </div>
        </div>
        <div style="flex:1; min-width:200px; background:#f0fdf4; border-radius:10px;
             padding:16px 18px; border:1px solid #bbf7d0;">
          <div style="font-size:13px; font-weight:700; color:#16a34a; margin-bottom:6px;">
            SILVER LAYER
          </div>
          <div style="font-size:14px; color:#374151;">
            Data cleaning, validation, and enrichment using PySpark transformations.
          </div>
        </div>
        <div style="flex:1; min-width:200px; background:#fffbeb; border-radius:10px;
             padding:16px 18px; border:1px solid #fde68a;">
          <div style="font-size:13px; font-weight:700; color:#d97706; margin-bottom:6px;">
            GOLD LAYER
          </div>
          <div style="font-size:14px; color:#374151;">
            Business KPIs generated using Spark SQL — same queries as the local SQLite layer.
          </div>
        </div>
      </div>
      <div style="margin-top:16px; background:#eff6ff; border-radius:10px; padding:14px 18px;
           border:1px solid #bfdbfe; font-size:15px; color:#1e40af; line-height:1.7;">
        This demonstrates how the project can be migrated from a local environment to an
        enterprise cloud platform <strong>without changing the business logic</strong> —
        only the execution engine changes.
      </div>
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# TAB 6 — ENGINEERING DECISIONS & PROJECT JOURNEY
# ──────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown('<div class="section-title">📝 Engineering Decisions &amp; Project Journey</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-sub">
      This section documents the architectural decisions, implementation choices, challenges
      encountered, and key learnings during the development of RetailPulse.
    </div>""", unsafe_allow_html=True)

    pj1, pj2 = st.columns(2)

    with pj1:
        # Card 1
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; margin-bottom:16px; border-top:4px solid #1a56db;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:14px;">Why Medallion Architecture?</div>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:0 0 12px 0;">
            RetailPulse follows the Medallion Architecture because it separates raw, cleaned,
            and business-ready data into independent layers.
          </p>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:0 0 10px 0;">
            This approach provides:
          </p>
          <ul style="font-size:15px; color:#374151; line-height:2.1; margin:0 0 12px 0; padding-left:18px;">
            <li>Improved maintainability</li>
            <li>Better data quality</li>
            <li>Easier debugging</li>
            <li>Reusable datasets</li>
            <li>Clear separation of responsibilities</li>
          </ul>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:0;">
            Each processing stage has a single responsibility:
            <strong>Bronze</strong> stores original source files.
            <strong>Silver</strong> performs cleaning, validation, and enrichment.
            <strong>Gold</strong> generates business-ready analytics and KPIs.
          </p>
        </div>""", unsafe_allow_html=True)

        # Card 3
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; border-top:4px solid #10b981;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:14px;">Challenges Solved</div>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:0 0 12px 0;">
            During development several technical issues were addressed:
          </p>
          <ul style="font-size:15px; color:#374151; line-height:2.1; margin:0; padding-left:18px;">
            <li>Missing values and duplicate records reduced data quality</li>
            <li>Inconsistent file naming was standardised</li>
            <li>Dynamic SQL filtering logic was corrected</li>
            <li>Visualisation themes were redesigned for better readability</li>
            <li>Inventory forecasting logic was improved to provide more realistic stock predictions</li>
          </ul>
          <div style="margin-top:14px; background:#f0fdf4; border-radius:10px; padding:12px 16px;
               font-size:14px; color:#166534; border:1px solid #bbf7d0;">
            These improvements increased pipeline reliability and overall usability.
          </div>
        </div>""", unsafe_allow_html=True)

    with pj2:
        # Card 2
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; margin-bottom:16px; border-top:4px solid #9061f9;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:14px;">Key Engineering Decisions</div>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:0 0 12px 0;">
            Several design choices were made to keep the project practical while following
            industry practices.
          </p>
          <div style="display:flex; flex-direction:column; gap:10px; font-size:15px;">
            <div style="background:#f8fafc; border-radius:10px; padding:11px 14px;
                 border-left:3px solid #1a56db; color:#374151;">
              Implemented Medallion Architecture for modular processing
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:11px 14px;
                 border-left:3px solid #9061f9; color:#374151;">
              Used SQLite to perform SQL analytics locally
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:11px 14px;
                 border-left:3px solid #10b981; color:#374151;">
              Generated KPIs using SQL instead of only Pandas to demonstrate database integration
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:11px 14px;
                 border-left:3px solid #f59e0b; color:#374151;">
              Built an interactive Streamlit dashboard for business users
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:11px 14px;
                 border-left:3px solid #ef4444; color:#374151;">
              Developed an equivalent PySpark implementation in Databricks to demonstrate scalability
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Card 4
        st.markdown("""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
             padding:26px; border-top:4px solid #f59e0b;">
          <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
               color:#0f172a; margin-bottom:14px;">Future Enhancements</div>
          <p style="font-size:15px; color:#374151; line-height:1.85; margin:0 0 12px 0;">
            RetailPulse can be extended further by integrating:
          </p>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:14px;">
            <div style="background:#fffbeb; border-radius:8px; padding:9px 13px;
                 color:#374151; border:1px solid #fde68a;">Azure Data Factory</div>
            <div style="background:#fffbeb; border-radius:8px; padding:9px 13px;
                 color:#374151; border:1px solid #fde68a;">Azure Blob Storage</div>
            <div style="background:#fffbeb; border-radius:8px; padding:9px 13px;
                 color:#374151; border:1px solid #fde68a;">Kafka Streaming</div>
            <div style="background:#fffbeb; border-radius:8px; padding:9px 13px;
                 color:#374151; border:1px solid #fde68a;">Delta Live Tables</div>
            <div style="background:#fffbeb; border-radius:8px; padding:9px 13px;
                 color:#374151; border:1px solid #fde68a;">Power BI Dashboards</div>
            <div style="background:#fffbeb; border-radius:8px; padding:9px 13px;
                 color:#374151; border:1px solid #fde68a;">ML Demand Forecasting</div>
            <div style="background:#fffbeb; border-radius:8px; padding:9px 13px;
                 color:#374151; border:1px solid #fde68a; grid-column:1/-1">
              Apache Airflow Scheduling</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Card 5 — Key Learning Outcomes (full width)
    st.markdown("""
    <div style="background:white; border:1px solid #e2e8f0; border-radius:14px;
         padding:26px; margin-top:4px; border-top:4px solid #16bdca;">
      <div style="font-family:'EB Garamond',serif; font-size:21px; font-weight:700;
           color:#0f172a; margin-bottom:16px;">Key Learning Outcomes</div>
      <p style="font-size:15px; color:#374151; line-height:1.85; margin:0 0 14px 0;">
        This project strengthened practical knowledge in:
      </p>
      <div style="display:flex; flex-wrap:wrap; gap:10px; font-size:14px;">
        <span style="background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe;
              border-radius:8px; padding:7px 14px; font-weight:600;">Data Engineering Pipelines</span>
        <span style="background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe;
              border-radius:8px; padding:7px 14px; font-weight:600;">ETL Design</span>
        <span style="background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe;
              border-radius:8px; padding:7px 14px; font-weight:600;">SQL Analytics</span>
        <span style="background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe;
              border-radius:8px; padding:7px 14px; font-weight:600;">Medallion Architecture</span>
        <span style="background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe;
              border-radius:8px; padding:7px 14px; font-weight:600;">Data Quality Management</span>
        <span style="background:#f0fdf4; color:#166534; border:1px solid #bbf7d0;
              border-radius:8px; padding:7px 14px; font-weight:600;">Streamlit Dashboard Development</span>
        <span style="background:#f5f0ff; color:#5b21b6; border:1px solid #ddd6fe;
              border-radius:8px; padding:7px 14px; font-weight:600;">PySpark</span>
        <span style="background:#f5f0ff; color:#5b21b6; border:1px solid #ddd6fe;
              border-radius:8px; padding:7px 14px; font-weight:600;">Databricks</span>
        <span style="background:#f5f0ff; color:#5b21b6; border:1px solid #ddd6fe;
              border-radius:8px; padding:7px 14px; font-weight:600;">Delta Lake</span>
        <span style="background:#fff7ed; color:#9a3412; border:1px solid #fed7aa;
              border-radius:8px; padding:7px 14px; font-weight:600;">Enterprise Data Processing</span>
      </div>
    </div>""", unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #e2e8f0; padding:28px 0 20px 0;">
  <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:16px;">
    <div>
      <div style="font-family:'EB Garamond',serif; font-size:22px; font-weight:800;
           color:#1a56db; letter-spacing:-0.5px; margin-bottom:3px;">RetailPulse</div>
      <div style="font-size:13px; font-weight:600; color:#475569; margin-bottom:8px;">
        Smart Metadata-Driven Retail Supply Chain Pipeline
      </div>
      <div style="font-size:12px; color:#94a3b8; line-height:1.7;">
        RetailPulse v1.0 &nbsp;·&nbsp; Final Major Project<br>
        Celebal Excellence Internship (CEI) &nbsp;·&nbsp; Developed by <strong style="color:#64748b;">Nithin Siga</strong>
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:12px; color:#cbd5e1; line-height:2;">
        Python &nbsp;·&nbsp; Pandas &nbsp;·&nbsp; SQLite &nbsp;·&nbsp; Plotly &nbsp;·&nbsp; Streamlit<br>
        PySpark &nbsp;·&nbsp; Databricks &nbsp;·&nbsp; Delta Lake
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
