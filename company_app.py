"""
Company Intelligence Hub - 826 Companies
Dark editorial UI matching Validation_500
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from anthropic import Anthropic
import os
import numpy as np

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Company Intelligence Hub",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium Dark CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

    * { font-family: 'DM Sans', sans-serif !important; }

    .stApp { background: #080b10; }

    .block-container {
        background: #0d1117;
        border-radius: 0px;
        padding: 2.5rem 3rem;
        border-left: 1px solid rgba(56, 189, 248, 0.08);
        max-width: 1400px;
    }

    [data-testid="stSidebar"] {
        background: #080b10;
        border-right: 1px solid rgba(56,189,248,0.08);
    }
    [data-testid="stSidebar"] * { color: #94a3b8 !important; }

    h1 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        font-size: 3.2rem !important;
        color: #f1f5f9 !important;
        letter-spacing: -0.04em !important;
        line-height: 1.1 !important;
        margin-bottom: 0.5rem !important;
    }
    h2 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        color: #e2e8f0 !important;
        letter-spacing: -0.02em !important;
        margin-top: 2.5rem !important;
    }
    h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
    }
    p, .stMarkdown p { color: #94a3b8 !important; font-size: 1rem !important; line-height: 1.7 !important; }

    div[data-testid="metric-container"] {
        background: #111827;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(56,189,248,0.1);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: rgba(56,189,248,0.3);
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(56,189,248,0.08);
    }
    [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: #64748b !important;
    }
    [data-testid="stMetricDelta"] { color: #34d399 !important; }

    .stButton > button {
        background: transparent;
        color: #38bdf8 !important;
        border: 1.5px solid rgba(56,189,248,0.4);
        border-radius: 8px;
        padding: 0.6rem 1.8rem;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        background: rgba(56,189,248,0.08);
        border-color: #38bdf8;
        box-shadow: 0 0 20px rgba(56,189,248,0.15);
    }

    [data-testid="stSidebar"] .stRadio > label {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.3rem 0;
        transition: all 0.25s ease;
        cursor: pointer;
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(56,189,248,0.06);
        border-color: rgba(56,189,248,0.2);
        transform: translateX(4px);
    }

    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stMultiSelect > div > div {
        background: #111827 !important;
        border: 1.5px solid rgba(56,189,248,0.15) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #111827;
        border-radius: 12px;
        padding: 0.4rem;
        gap: 6px;
        border: 1px solid rgba(56,189,248,0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
        color: #64748b;
        background: transparent;
        border: none;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(56,189,248,0.12) !important;
        color: #38bdf8 !important;
        box-shadow: 0 0 16px rgba(56,189,248,0.1);
    }

    .stAlert {
        background: #111827 !important;
        border-radius: 12px !important;
        border-left: 4px solid #38bdf8 !important;
        color: #94a3b8 !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        border: 1px solid rgba(56,189,248,0.1);
        overflow: hidden;
    }

    .streamlit-expanderHeader {
        background: #111827;
        border-radius: 10px;
        color: #94a3b8 !important;
        border: 1px solid rgba(56,189,248,0.08);
        font-weight: 600;
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(56,189,248,0.2) 50%, transparent 100%);
        margin: 2.5rem 0;
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #080b10; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

    .js-plotly-plot {
        border-radius: 16px !important;
        border: 1px solid rgba(56,189,248,0.08) !important;
    }

    code {
        background: #111827;
        color: #38bdf8;
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.85em;
        border: 1px solid rgba(56,189,248,0.15);
    }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .element-container { animation: fadeUp 0.4s ease both; }

    .accent-line {
        width: 60px; height: 4px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        border-radius: 2px;
        margin-bottom: 1.5rem;
    }
    .badge {
        display: inline-block;
        background: rgba(56,189,248,0.1);
        color: #38bdf8;
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
DB_PATH = "company_intelligence.db"

PLOT_LAYOUT = dict(
    plot_bgcolor='#111827', paper_bgcolor='#111827',
    font=dict(color='#94a3b8'),
    xaxis=dict(showgrid=False, color='#475569', zeroline=False),
    yaxis=dict(showgrid=False, color='#475569'),
    margin=dict(l=0, r=40, t=10, b=10),
)

if not CLAUDE_API_KEY:
    st.error("Please set CLAUDE_API_KEY environment variable before running")
    st.stop()

client = Anthropic(api_key=CLAUDE_API_KEY)

# ── Data helpers ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM companies", conn)
    conn.close()
    return df

@st.cache_data
def get_company_names():
    df = load_data()
    return sorted(df['company_name'].dropna().tolist())

def get_company_details(company_name):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM companies WHERE company_name = ?", conn, params=(company_name,))
    conn.close()
    return df.iloc[0] if len(df) > 0 else None

def find_competitors(company_name):
    company = get_company_details(company_name)
    if company is None:
        return pd.DataFrame()
    industry = company['claude_industry']
    location = company['claude_location']
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT company_name, claude_industry, claude_location,
               claude_funding_stage, claude_company_size, claude_hei_found
        FROM companies
        WHERE company_name != ? AND claude_status = 'done'
        AND (LOWER(claude_industry) LIKE LOWER(?) OR LOWER(claude_location) LIKE LOWER(?))
        LIMIT 15
    """, conn, params=(company_name, f"%{industry}%", f"%{location}%"))
    conn.close()
    return df

def calculate_hei_penetration():
    df = load_data()
    df_c = df[df['claude_status'] == 'done'].copy()
    stats = df_c.groupby('claude_industry').agg(
        Total_Companies=('company_name', 'count'),
        HEI_Partners=('claude_hei_found', lambda x: (x == 'Yes').sum())
    ).reset_index()
    stats.columns = ['Industry', 'Total_Companies', 'HEI_Partners']
    stats['Penetration_Rate'] = (stats['HEI_Partners'] / stats['Total_Companies'] * 100).round(1)
    return stats.sort_values('Penetration_Rate', ascending=False)

def get_industry_benchmarks(industry):
    df = load_data()
    ind_df = df[df['claude_industry'] == industry]
    if len(ind_df) == 0:
        return None
    hei_rate = (ind_df['claude_hei_found'] == 'Yes').sum() / len(ind_df) * 100
    funding_dist = ind_df['claude_funding_stage'].value_counts()
    size_dist = ind_df['claude_company_size'].value_counts()
    return {
        'total_companies': len(ind_df),
        'hei_penetration': round(hei_rate, 1),
        'common_funding_stage': funding_dist.index[0] if len(funding_dist) > 0 else "Unknown",
        'typical_size': size_dist.index[0] if len(size_dist) > 0 else "Unknown"
    }

def identify_market_opportunities():
    stats = calculate_hei_penetration()
    stats = stats[stats['Total_Companies'] >= 5].copy()
    stats['Opportunity_Score'] = (
        stats['Total_Companies'] / stats['Total_Companies'].max() * 50 +
        (100 - stats['Penetration_Rate']) / 100 * 50
    ).round(1)
    return stats.sort_values('Opportunity_Score', ascending=False)

# ── AI Agent ──────────────────────────────────────────────────────────────────
SCHEMA = """
Table: companies
Columns: company_name, claude_industry, claude_location, claude_founded_year,
claude_company_size, claude_funding_stage, claude_description,
claude_hei_found (Yes/No), claude_hei_institutions, confidence_level (High/Medium/Low)
"""

def generate_sql(user_query):
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=500,
        messages=[{"role": "user", "content":
            f"Convert to SQLite SQL using claude_* columns.\n{SCHEMA}\nQuery: {user_query}\nReturn ONLY SQL. Limit 50 results."}]
    )
    return response.content[0].text.strip().replace("```sql","").replace("```","").strip()

def execute_query(sql):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(sql, conn); conn.close(); return df, None
    except Exception as e:
        conn.close(); return None, str(e)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='padding: 1rem 0 0.5rem 0;'>
    <div style='font-family: Syne, sans-serif; font-size: 1.1rem; font-weight: 800; color: #38bdf8; letter-spacing: -0.02em;'>Company Intelligence</div>
    <div style='font-size: 0.75rem; color: #475569; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.2rem;'>826 Company Dataset</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", [
    "🏠 Overview", "💬 AI Agent Chat", "🔎 Company Lookup",
    "🎯 Divergence", "📈 Market Opportunity", "📊 KPI Dashboard", "📉 Analytics"
])

df_all = load_data()
df_done = df_all[df_all['claude_status'] == 'done']

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='padding: 0.5rem 0;'>
    <div style='font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.8rem;'>Dataset</div>
    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
        <span style='color: #64748b; font-size: 0.85rem;'>Total</span>
        <span style='color: #38bdf8; font-weight: 600; font-size: 0.85rem;'>{len(df_all)}</span>
    </div>
    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
        <span style='color: #64748b; font-size: 0.85rem;'>Enriched</span>
        <span style='color: #34d399; font-weight: 600; font-size: 0.85rem;'>{len(df_done)}</span>
    </div>
    <div style='display: flex; justify-content: space-between;'>
        <span style='color: #64748b; font-size: 0.85rem;'>HEI Found</span>
        <span style='color: #a78bfa; font-weight: 600; font-size: 0.85rem;'>{(df_all['claude_hei_found']=='Yes').sum()}</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.7rem; color: #334155; text-transform: uppercase; letter-spacing: 0.08em;'>
MS Business Analytics<br>Worcester Polytechnic Institute
</div>
""", unsafe_allow_html=True)

# ── PAGE 1: Overview ──────────────────────────────────────────────────────────
if page == "🏠 Overview":
    st.markdown('<div class="badge">826 Company Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("Company Intelligence")
    st.markdown("**Dual-model enrichment pipeline** — Claude Sonnet · GPT-4o · Web Scraping")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Companies", len(df_all))
    with col2: st.metric("Enriched", len(df_done), delta=f"{len(df_done)/826*100:.1f}%")
    with col3: st.metric("HEI Partnerships", (df_all['claude_hei_found']=='Yes').sum())
    with col4: st.metric("Divergent", "72")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top Industries")
        top_ind = df_all['claude_industry'].value_counts().head(10)
        fig = go.Figure(go.Bar(
            x=top_ind.values[::-1], y=top_ind.index[::-1], orientation='h',
            marker=dict(color=top_ind.values[::-1], colorscale=[[0,'#1e3a5f'],[1,'#38bdf8']], showscale=False),
            text=top_ind.values[::-1], textposition='outside', textfont=dict(color='#64748b', size=12)
        ))
        fig.update_layout(**PLOT_LAYOUT, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### HEI Partnership Split")
        hei_yes = (df_all['claude_hei_found']=='Yes').sum()
        fig = go.Figure(go.Pie(
            labels=['With HEI Partners', 'Without HEI Partners'],
            values=[hei_yes, len(df_done)-hei_yes],
            hole=0.6,
            marker=dict(colors=['#38bdf8', '#1e293b']),
            textfont=dict(color='#e2e8f0', size=13)
        ))
        fig.update_layout(
            plot_bgcolor='#111827', paper_bgcolor='#111827',
            legend=dict(font=dict(color='#94a3b8'), bgcolor='#111827'),
            margin=dict(l=0,r=0,t=10,b=10), height=380
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Model Agreement")
        agree = df_all['confidence_level'].value_counts()
        fig = go.Figure(go.Pie(
            labels=agree.index, values=agree.values, hole=0.5,
            marker=dict(colors=['#34d399','#38bdf8','#475569']),
            textfont=dict(color='#e2e8f0')
        ))
        fig.update_layout(plot_bgcolor='#111827', paper_bgcolor='#111827',
            legend=dict(font=dict(color='#94a3b8'), bgcolor='#111827'),
            margin=dict(l=0,r=0,t=10,b=10), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Funding Stage")
        funding = df_done[df_done['claude_funding_stage']!='Unknown']['claude_funding_stage'].value_counts()
        fig = go.Figure(go.Bar(
            x=funding.index, y=funding.values,
            marker=dict(color=funding.values, colorscale=[[0,'#1e1b4b'],[1,'#818cf8']], showscale=False),
            text=funding.values, textposition='outside', textfont=dict(color='#64748b')
        ))
        fig.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.markdown("### Company Size")
        size_order = ['1-10','11-50','51-200','201-500','500+']
        size_data = df_done[df_done['claude_company_size'].isin(size_order)]['claude_company_size'].value_counts()
        size_data = size_data.reindex(size_order).dropna()
        fig = go.Figure(go.Bar(
            x=size_data.index, y=size_data.values,
            marker=dict(color=size_data.values, colorscale=[[0,'#164e63'],[1,'#34d399']], showscale=False),
            text=size_data.values, textposition='outside', textfont=dict(color='#64748b')
        ))
        fig.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.info("**Key findings:** 57 funding/size anomalies · 10 HEI divergence outliers · 3 multi-dimensional outliers · 8 geographically concentrated industries")

# ── PAGE 2: AI Agent Chat ─────────────────────────────────────────────────────
elif page == "💬 AI Agent Chat":
    st.markdown('<div class="badge">Natural Language Query</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("AI Agent Chat")
    st.markdown("Ask questions in plain English — Claude generates SQL and queries the database.")
    st.markdown("---")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    examples = ["Show me all EdTech companies", "Which companies have university partners?",
                "List companies in California", "Find Series A funded companies", "Companies founded after 2020"]

    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        if cols[i].button(ex, key=f"ex_{i}"):
            st.session_state.user_query = ex

    user_query = st.text_input("Your question:", key="query_input",
                               value=st.session_state.get('user_query', ''),
                               placeholder="e.g. Which EdTech companies are Series B funded?")

    if st.button("Search", key="search_btn") and user_query:
        with st.spinner("Generating SQL..."):
            sql = generate_sql(user_query)
            st.code(sql, language="sql")
            results_df, error = execute_query(sql)
            if error:
                st.error(f"Error: {error}")
            elif results_df is not None and len(results_df) > 0:
                st.success(f"Found {len(results_df)} results")
                st.dataframe(results_df, use_container_width=True)
                st.session_state.chat_history.append({'query': user_query, 'sql': sql, 'results': len(results_df)})
            else:
                st.warning("No results found")

    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### Recent Queries")
        for item in reversed(st.session_state.chat_history[-5:]):
            with st.expander(f"{item['query']} ({item['results']} results)"):
                st.code(item['sql'], language="sql")

# ── PAGE 3: Company Lookup ────────────────────────────────────────────────────
elif page == "🔎 Company Lookup":
    st.markdown('<div class="badge">Company Profile & Benchmarking</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("Company Lookup")
    st.markdown("---")

    company_name = st.selectbox("Select a company", [""] + get_company_names())

    if company_name:
        company = get_company_details(company_name)
        if company is not None:
            st.markdown(f"## {company_name}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Industry", company['claude_industry'] or "Unknown")
                st.metric("Location", company['claude_location'] or "Unknown")
            with col2:
                st.metric("Founded", company['claude_founded_year'] or "Unknown")
                st.metric("Company Size", company['claude_company_size'] or "Unknown")
            with col3:
                st.metric("Funding Stage", company['claude_funding_stage'] or "Unknown")
                st.metric("HEI Partners", company['claude_hei_found'] or "Unknown")

            st.markdown("---")
            st.markdown("### Description")
            st.write(company['claude_description'] or "No description available")

            if company['claude_hei_found'] == 'Yes' and company['claude_hei_institutions']:
                st.markdown("### University / HEI Partners")
                st.info(company['claude_hei_institutions'])

            st.markdown("---")
            st.markdown("### Industry Benchmarking")

            benchmarks = get_industry_benchmarks(company['claude_industry'])
            if benchmarks:
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Industry Peers", benchmarks['total_companies'])
                with col2: st.metric("Industry HEI Avg", f"{benchmarks['hei_penetration']}%",
                                     delta=f"This co: {company['claude_hei_found']}")
                with col3: st.metric("Common Funding", benchmarks['common_funding_stage'])
                with col4: st.metric("Typical Size", benchmarks['typical_size'])

                has_hei = company['claude_hei_found'] == 'Yes'
                avg = benchmarks['hei_penetration']
                if has_hei and avg < 50:
                    st.success(f"Competitive Advantage: HEI partner while only {avg}% of peers are")
                elif not has_hei and avg > 50:
                    st.warning(f"Opportunity Gap: {avg}% of peers have HEI partners — this company doesn't")
                elif has_hei:
                    st.info(f"On par with industry — {avg}% of peers also have HEI partners")
                else:
                    st.info(f"Standard — no HEI partners (industry avg: {avg}%)")

            st.markdown("---")
            st.markdown("### Model Agreement")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Industry Match", company['industry_agreement'] or "Unknown")
            with col2: st.metric("Location Match", company['location_agreement'] or "Unknown")
            with col3: st.metric("Confidence", company['confidence_level'] or "Unknown")

            st.markdown("---")
            st.markdown("### Similar Companies")
            competitors = find_competitors(company_name)
            if len(competitors) > 0:
                st.dataframe(competitors, use_container_width=True)
                c_with_hei = (competitors['claude_hei_found']=='Yes').sum()
                col1, col2 = st.columns(2)
                with col1: st.metric("Similar Companies Found", len(competitors))
                with col2: st.metric("With HEI Partners", f"{c_with_hei} ({c_with_hei/len(competitors)*100:.0f}%)")
            else:
                st.info("No similar companies found")

# ── PAGE 4: Divergence ────────────────────────────────────────────────────────
elif page == "🎯 Divergence":
    st.markdown('<div class="badge">Outlier & Anomaly Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("Divergence Analysis")
    st.markdown("Companies that don't fit standard patterns — outliers in funding, size, or HEI engagement.")
    st.markdown("---")

    df = load_data()
    df_c = df[df['claude_status'] == 'done'].copy()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Funding/Size Anomalies", "57")
    with col2: st.metric("Industry Outliers", "5")
    with col3: st.metric("HEI Divergence", "10")
    with col4: st.metric("Multi-Dimensional", "3")

    st.markdown("---")

    def extract_size_num(s):
        return {"1-10":5,"11-50":30,"51-200":125,"201-500":350,"500+":750}.get(s)
    def extract_fund_num(s):
        return {"Bootstrapped":0,"Seed":1,"Series A":2,"Series B":3,"Series C":4,"Public":5}.get(s)

    df_c['size_num'] = df_c['claude_company_size'].apply(extract_size_num)
    df_c['fund_num'] = df_c['claude_funding_stage'].apply(extract_fund_num)

    tab1, tab2, tab3 = st.tabs(["💰 Funding Anomalies", "📏 Industry Outliers", "🎓 HEI Divergence"])

    with tab1:
        anomalies = []
        for _, row in df_c.iterrows():
            s, f = row['size_num'], row['fund_num']
            if pd.isna(s) or pd.isna(f): continue
            if s <= 30 and f >= 3:
                anomalies.append({'Company': row['company_name'], 'Industry': row['claude_industry'],
                    'Size': row['claude_company_size'], 'Funding': row['claude_funding_stage'],
                    'Pattern': 'Late-stage funding, small team'})
            elif s >= 350 and f <= 1:
                anomalies.append({'Company': row['company_name'], 'Industry': row['claude_industry'],
                    'Size': row['claude_company_size'], 'Funding': row['claude_funding_stage'],
                    'Pattern': 'Large team, minimal funding'})
        if anomalies:
            adf = pd.DataFrame(anomalies)
            st.markdown(f"**{len(adf)} companies** with unusual funding/size combinations")
            st.dataframe(adf, use_container_width=True, height=500)
        else:
            st.info("No funding anomalies detected")

    with tab2:
        from scipy import stats
        outliers = []
        for industry in df_c['claude_industry'].value_counts().head(15).index:
            idf = df_c[df_c['claude_industry'] == industry].copy()
            if len(idf) < 5: continue
            valid = idf['size_num'].dropna()
            if len(valid) < 3: continue
            idf.loc[idf['size_num'].notna(), 'size_zscore'] = stats.zscore(valid)
            for _, row in idf[abs(idf['size_zscore'].fillna(0)) > 2].iterrows():
                outliers.append({'Company': row['company_name'], 'Industry': industry,
                    'Size': row['claude_company_size'],
                    'Deviation': 'Much larger than peers' if row['size_zscore'] > 0 else 'Much smaller',
                    'Z-Score': f"{row['size_zscore']:.2f}"})
        if outliers:
            st.markdown(f"**{len(outliers)} companies** are statistical outliers (>2 std dev from industry mean)")
            st.dataframe(pd.DataFrame(outliers), use_container_width=True, height=500)
        else:
            st.info("No significant industry outliers detected")

    with tab3:
        ind_hei = df_c.groupby('claude_industry').apply(
            lambda x: (x['claude_hei_found']=='Yes').sum()/len(x)*100 if len(x)>0 else 0
        ).to_dict()
        hei_div = []
        for _, row in df_c.iterrows():
            ind = row['claude_industry']
            rate = ind_hei.get(ind, 0)
            has = row['claude_hei_found'] == 'Yes'
            if has and rate < 20:
                hei_div.append({'Company': row['company_name'], 'Industry': ind,
                    'HEI Found': 'Yes', 'Industry Avg': f"{rate:.0f}%",
                    'Pattern': 'HEI leader in non-traditional sector'})
            elif not has and rate > 60:
                hei_div.append({'Company': row['company_name'], 'Industry': ind,
                    'HEI Found': 'No', 'Industry Avg': f"{rate:.0f}%",
                    'Pattern': 'Missing partnerships common in sector'})
        if hei_div:
            st.markdown(f"**{len(hei_div)} companies** with divergent HEI patterns")
            st.dataframe(pd.DataFrame(hei_div), use_container_width=True, height=500)
        else:
            st.info("No significant HEI divergence detected")

# ── PAGE 5: Market Opportunity ────────────────────────────────────────────────
elif page == "📈 Market Opportunity":
    st.markdown('<div class="badge">Untapped Markets</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("Market Opportunity")
    st.markdown("High company count + Low HEI penetration = Untapped market potential.")
    st.markdown("---")

    opps = identify_market_opportunities()

    st.markdown("### Top Opportunities")
    top10 = opps.head(10)[['Industry','Total_Companies','HEI_Partners','Penetration_Rate','Opportunity_Score']]
    st.dataframe(top10, use_container_width=True)

    st.markdown("---")
    st.markdown("### Opportunity Matrix")

    fig = go.Figure(go.Scatter(
        x=opps['Penetration_Rate'], y=opps['Total_Companies'],
        mode='markers+text',
        marker=dict(size=opps['Opportunity_Score']/2, color=opps['Opportunity_Score'],
                    colorscale=[[0,'#1e3a5f'],[1,'#38bdf8']], showscale=True,
                    colorbar=dict(title='Score', tickfont=dict(color='#94a3b8'))),
        text=opps['Industry'], textposition='top center',
        textfont=dict(color='#64748b', size=10),
        hovertemplate='<b>%{text}</b><br>Penetration: %{x}%<br>Companies: %{y}<extra></extra>'
    ))
    fig.add_hline(y=opps['Total_Companies'].median(), line_dash="dash", line_color="#475569")
    fig.add_vline(x=opps['Penetration_Rate'].median(), line_dash="dash", line_color="#475569")
    fig.update_layout(**PLOT_LAYOUT,
        xaxis_title="HEI Penetration Rate (%)", yaxis_title="Market Size (Companies)", height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Industry Deep Dive")
    selected = st.selectbox("Select industry", opps['Industry'].tolist())
    if selected:
        row = opps[opps['Industry']==selected].iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total Companies", int(row['Total_Companies']))
        with col2: st.metric("With HEI Partners", int(row['HEI_Partners']))
        with col3: st.metric("Penetration Rate", f"{row['Penetration_Rate']}%")
        st.markdown(f"**Opportunity Score: {row['Opportunity_Score']}/100**")
        df_temp = load_data()
        ind_cos = df_temp[df_temp['claude_industry']==selected][
            ['company_name','claude_hei_found','claude_funding_stage','claude_location']]
        st.dataframe(ind_cos, use_container_width=True)

# ── PAGE 6: KPI Dashboard ─────────────────────────────────────────────────────
elif page == "📊 KPI Dashboard":
    st.markdown('<div class="badge">Business KPIs</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("KPI Dashboard")
    st.markdown("---")

    df = load_data()
    df_c = df[df['claude_status'] == 'done'].copy()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Enriched Companies", len(df_c), delta=f"{len(df_c)/826*100:.1f}%")
    with col2:
        hei_ct = (df_c['claude_hei_found']=='Yes').sum()
        st.metric("HEI Partnerships", hei_ct, delta=f"{hei_ct/len(df_c)*100:.1f}% rate")
    with col3:
        ind_counts = df_c['claude_industry'].value_counts()
        top5 = ind_counts.head(5).sum()/len(df_c)*100
        st.metric("Top 5 Concentration", f"{top5:.1f}%")
    with col4: st.metric("Unique Industries", df_c['claude_industry'].nunique())

    st.markdown("---")
    st.markdown("### HEI Penetration by Industry")

    pen = calculate_hei_penetration().head(15)
    fig = go.Figure(go.Bar(
        x=pen['Penetration_Rate'][::-1], y=pen['Industry'][::-1], orientation='h',
        marker=dict(color=pen['Penetration_Rate'][::-1],
                    colorscale=[[0,'#1e3a5f'],[0.5,'#38bdf8'],[1,'#34d399']], showscale=False),
        text=[f"{r}%" for r in pen['Penetration_Rate'][::-1]],
        textposition='outside', textfont=dict(color='#64748b')
    ))
    fig.update_layout(**PLOT_LAYOUT, height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Data Quality")
    col1, col2, col3 = st.columns(3)
    with col1:
        high_conf = (df_c['confidence_level']=='High').sum()
        st.metric("High Confidence", high_conf, delta=f"{high_conf/len(df_c)*100:.1f}%")
    with col2:
        dual = ((df_c['claude_status']=='done') & (df_c['gpt_status']=='done')).sum()
        st.metric("Dual-Model Validated", dual, delta=f"{dual/len(df_c)*100:.1f}%")
    with col3:
        scraped = (df_c['scrape_status']=='done').sum()
        st.metric("Web Scraped", scraped, delta=f"{scraped/len(df_c)*100:.1f}%")

# ── PAGE 7: Analytics ─────────────────────────────────────────────────────────
elif page == "📉 Analytics":
    st.markdown('<div class="badge">Visual Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.title("Analytics")
    st.markdown("---")

    df = load_data()
    df_c = df[(df['claude_status']=='done') & (df['gpt_status']=='done')].copy()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Top 10 Industries")
        top_ind = df_c['claude_industry'].value_counts().head(10)
        fig = go.Figure(go.Bar(
            x=top_ind.values[::-1], y=top_ind.index[::-1], orientation='h',
            marker=dict(color=top_ind.values[::-1], colorscale=[[0,'#1e3a5f'],[1,'#38bdf8']], showscale=False),
            text=top_ind.values[::-1], textposition='outside', textfont=dict(color='#64748b')
        ))
        fig.update_layout(**PLOT_LAYOUT, height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Geographic Distribution")
        def extract_country(loc):
            if pd.isna(loc) or loc == "Unknown": return "Unknown"
            parts = str(loc).split(',')
            return parts[-1].strip() if len(parts) >= 2 else str(loc)
        df_c['country'] = df_c['claude_location'].apply(extract_country)
        geo = df_c[df_c['country']!='Unknown']['country'].value_counts().head(10)
        fig = go.Figure(go.Pie(
            labels=geo.index, values=geo.values, hole=0.5,
            marker=dict(colors=['#38bdf8','#818cf8','#34d399','#f472b6',
                               '#f59e0b','#06b6d4','#a78bfa','#fb7185','#4ade80','#fbbf24']),
            textfont=dict(color='#e2e8f0', size=12)
        ))
        fig.update_layout(plot_bgcolor='#111827', paper_bgcolor='#111827',
            legend=dict(font=dict(color='#94a3b8'), bgcolor='#111827'),
            margin=dict(l=0,r=0,t=10,b=10), height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Funding Stage")
        funding = df_c[df_c['claude_funding_stage']!='Unknown']['claude_funding_stage'].value_counts()
        fig = go.Figure(go.Bar(
            x=funding.index, y=funding.values,
            marker=dict(color=funding.values, colorscale=[[0,'#1e1b4b'],[1,'#818cf8']], showscale=False),
            text=funding.values, textposition='outside', textfont=dict(color='#64748b')
        ))
        fig.update_layout(**PLOT_LAYOUT, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Company Size")
        size_order = ['1-10','11-50','51-200','201-500','500+']
        size_data = df_c[df_c['claude_company_size'].isin(size_order)]['claude_company_size'].value_counts()
        size_data = size_data.reindex(size_order).dropna()
        fig = go.Figure(go.Bar(
            x=size_data.index, y=size_data.values,
            marker=dict(color=size_data.values, colorscale=[[0,'#164e63'],[1,'#34d399']], showscale=False),
            text=size_data.values, textposition='outside', textfont=dict(color='#64748b')
        ))
        fig.update_layout(**PLOT_LAYOUT, height=350)
        st.plotly_chart(fig, use_container_width=True)
