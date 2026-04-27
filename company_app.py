"""
Company Intelligence Streamlit App - Enhanced BA Edition
- AI Agent Chat Interface
- Company Lookup & Competitor Benchmarking
- Market Opportunity Analysis
- KPI Framework Dashboard
- Visual Analytics
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from anthropic import Anthropic
import os
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Company Intelligence Hub",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium CSS Styling ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif !important; }

    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
    }
    @keyframes gradientBG {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .block-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 28px;
        padding: 3rem 3rem 2rem 3rem;
        backdrop-filter: blur(30px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.2);
        margin-top: 1.5rem;
        margin-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * { color: #f0f0f0 !important; }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 60%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 2.6rem !important;
        letter-spacing: -0.03em;
    }
    h2 { color: #1a1a2e; font-weight: 700; font-size: 1.6rem !important; margin-top: 2rem; }
    h3 { color: #302b63; font-weight: 600; font-size: 1.15rem !important; }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(102,126,234,0.06) 0%, rgba(118,75,162,0.06) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1.5px solid rgba(102,126,234,0.12);
        transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
        box-shadow: 0 2px 12px rgba(102,126,234,0.05);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 32px rgba(102,126,234,0.18);
        border-color: rgba(102,126,234,0.35);
    }
    [data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #888 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 14px;
        padding: 0.7rem 2.2rem;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
        box-shadow: 0 6px 20px rgba(102,126,234,0.35);
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(102,126,234,0.55);
    }
    [data-testid="stSidebar"] .stRadio > label {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 0.85rem 1.2rem;
        margin: 0.35rem 0;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(102,126,234,0.25);
        transform: translateX(6px);
    }
    [data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
        border: 1.5px solid rgba(102,126,234,0.1);
    }
    .stAlert {
        border-radius: 16px;
        border-left: 5px solid;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        border-radius: 14px !important;
        border: 2px solid rgba(102,126,234,0.18) !important;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(102,126,234,0.05);
        padding: 0.5rem;
        border-radius: 18px;
        border: 1px solid rgba(102,126,234,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        font-size: 0.9rem;
        color: #667eea;
        background: transparent;
        border: none;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102,126,234,0.35);
    }
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(102,126,234,0.07) 0%, rgba(118,75,162,0.07) 100%);
        border-radius: 14px;
        font-weight: 600;
        padding: 1rem 1.5rem;
        border: 1px solid rgba(102,126,234,0.1);
    }
    .js-plotly-plot {
        border-radius: 20px !important;
        box-shadow: 0 6px 24px rgba(0,0,0,0.08) !important;
    }
    code {
        background: linear-gradient(135deg, rgba(102,126,234,0.08) 0%, rgba(118,75,162,0.08) 100%);
        border-radius: 8px;
        padding: 0.25rem 0.6rem;
        color: #764ba2;
        font-weight: 500;
        border: 1px solid rgba(102,126,234,0.15);
    }
    hr {
        margin: 2.5rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, rgba(102,126,234,0.25) 50%, transparent 100%);
    }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.04); border-radius: 8px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .element-container { animation: fadeInUp 0.4s ease-out both; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
DB_PATH = "company_intelligence.db"

# ── Initialize ────────────────────────────────────────────────────────────────
if not CLAUDE_API_KEY:
    st.error("⚠️ Please set CLAUDE_API_KEY environment variable before running")
    st.stop()

client = Anthropic(api_key=CLAUDE_API_KEY)

# ── Database helpers ──────────────────────────────────────────────────────────
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
    query = "SELECT * FROM companies WHERE company_name = ?"
    df = pd.read_sql(query, conn, params=(company_name,))
    conn.close()
    return df.iloc[0] if len(df) > 0 else None

def find_competitors(company_name):
    company = get_company_details(company_name)
    if company is None:
        return pd.DataFrame()
    
    industry = company['claude_industry']
    location = company['claude_location']
    
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT company_name, claude_industry, claude_location, 
               claude_funding_stage, claude_company_size, claude_hei_found
        FROM companies
        WHERE company_name != ?
        AND (LOWER(claude_industry) LIKE LOWER(?) OR LOWER(claude_location) LIKE LOWER(?))
        AND claude_status = 'done'
        LIMIT 15
    """
    df = pd.read_sql(query, conn, params=(company_name, f"%{industry}%", f"%{location}%"))
    conn.close()
    return df

# ── Business Analytics Functions ──────────────────────────────────────────────
def calculate_hei_penetration():
    """Calculate HEI penetration rate by industry"""
    df = load_data()
    df_complete = df[df['claude_status'] == 'done'].copy()
    
    industry_stats = df_complete.groupby('claude_industry').agg({
        'company_name': 'count',
        'claude_hei_found': lambda x: (x == 'Yes').sum()
    }).reset_index()
    
    industry_stats.columns = ['Industry', 'Total_Companies', 'HEI_Partners']
    industry_stats['Penetration_Rate'] = (industry_stats['HEI_Partners'] / industry_stats['Total_Companies'] * 100).round(1)
    industry_stats = industry_stats.sort_values('Penetration_Rate', ascending=False)
    
    return industry_stats

def get_industry_benchmarks(industry):
    """Get industry average metrics for benchmarking"""
    df = load_data()
    df_industry = df[df['claude_industry'] == industry].copy()
    
    if len(df_industry) == 0:
        return None
    
    # Calculate benchmarks
    hei_rate = (df_industry['claude_hei_found'] == 'Yes').sum() / len(df_industry) * 100
    
    # Funding stage distribution
    funding_dist = df_industry['claude_funding_stage'].value_counts()
    most_common_stage = funding_dist.index[0] if len(funding_dist) > 0 else "Unknown"
    
    # Company size distribution
    size_dist = df_industry['claude_company_size'].value_counts()
    avg_size = size_dist.index[0] if len(size_dist) > 0 else "Unknown"
    
    return {
        'total_companies': len(df_industry),
        'hei_penetration': round(hei_rate, 1),
        'common_funding_stage': most_common_stage,
        'typical_size': avg_size
    }

def calculate_market_concentration():
    """Calculate market concentration metrics"""
    df = load_data()
    df_complete = df[df['claude_status'] == 'done'].copy()
    
    industry_counts = df_complete['claude_industry'].value_counts()
    top_5_share = (industry_counts.head(5).sum() / len(df_complete) * 100).round(1)
    
    return {
        'top_5_concentration': top_5_share,
        'total_industries': len(industry_counts),
        'largest_industry': industry_counts.index[0],
        'largest_industry_count': industry_counts.iloc[0]
    }

def identify_market_opportunities():
    """Identify underserved markets with high potential"""
    industry_stats = calculate_hei_penetration()
    
    # Filter industries with at least 5 companies for statistical relevance
    industry_stats = industry_stats[industry_stats['Total_Companies'] >= 5].copy()
    
    # Define opportunity score: High company count + Low HEI penetration = Opportunity
    industry_stats['Opportunity_Score'] = (
        industry_stats['Total_Companies'] / industry_stats['Total_Companies'].max() * 50 +
        (100 - industry_stats['Penetration_Rate']) / 100 * 50
    ).round(1)
    
    return industry_stats.sort_values('Opportunity_Score', ascending=False)

# ── AI Agent Functions ────────────────────────────────────────────────────────
SCHEMA = """
Table: companies
Columns:
  - company_name (TEXT)
  - claude_industry (TEXT)
  - claude_location (TEXT)
  - claude_founded_year (TEXT)
  - claude_company_size (TEXT)
  - claude_funding_stage (TEXT)
  - claude_description (TEXT)
  - claude_hei_found (TEXT): Yes/No
  - claude_hei_institutions (TEXT)
  - confidence_level (TEXT): High/Medium/Low
"""

def generate_sql(user_query):
    prompt = f"""Convert this natural language query to SQLite SQL. Use claude_* columns as primary source.

{SCHEMA}

Query: {user_query}

Return ONLY the SQL query, nothing else. Limit to 50 results."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    sql = response.content[0].text.strip().replace("```sql", "").replace("```", "").strip()
    return sql

def execute_query(sql):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        conn.close()
        return None, str(e)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🔍 Company Intelligence Hub")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Overview", "💬 AI Agent Chat", "🔎 Company Lookup", 
     "🎯 Company Divergence", "📈 Market Opportunity", "📊 KPI Dashboard", "📉 Visual Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Dataset Summary")
df_all = load_data()
st.sidebar.metric("Total Companies", len(df_all))
st.sidebar.metric("Enriched", len(df_all[df_all['claude_status'] == 'done']))
st.sidebar.metric("HEI Partners Found", len(df_all[df_all['claude_hei_found'] == 'Yes']))

# ── PAGE 1: Overview ──────────────────────────────────────────────────────────
if page == "🏠 Overview":
    st.title("🏠 Company Intelligence Dashboard")
    st.markdown("### Project Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", "826")
    with col2:
        st.metric("Enriched Companies", "820")
    with col3:
        st.metric("HEI Partnerships", "179")
    with col4:
        st.metric("Divergent Companies", "72")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Company Divergence Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Funding/Size Anomalies", "57", 
                 help="Companies with unusual funding stage vs team size")
    
    with col2:
        st.metric("Industry Outliers", "5",
                 help="Companies significantly larger/smaller than industry peers")
    
    with col3:
        st.metric("HEI Divergence", "10",
                 help="Companies breaking industry norms for university partnerships")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏢 Top Industries by Company Count")
        top_industries = df_all['claude_industry'].value_counts().head(8)
        fig = px.bar(y=top_industries.index, x=top_industries.values, orientation='h',
                    labels={'x': 'Number of Companies', 'y': 'Industry'})
        fig.update_traces(marker_color='#667eea')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎓 HEI Partnership Distribution")
        hei_data = pd.DataFrame({
            'Category': ['With HEI Partners', 'Without HEI Partners'],
            'Count': [179, 820-179]
        })
        fig = px.pie(hei_data, values='Count', names='Category', 
                    color_discrete_sequence=['#667eea', '#e0e0e0'], hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 💡 Key Insights")
    st.success("""
    **Divergent Companies Identified:**
    - **57 companies** show unusual funding/size combinations (late-stage funding with small teams, or large teams with minimal funding)
    - **3 multi-dimensional outliers** divergent in 2+ ways — warrant deeper investigation
    - **10 companies** have unexpected HEI engagement patterns for their industry
    - **8 industries** show strong geographic concentration (>70% in single country)
    """)
    
    st.info("""
    **Data Quality:**
    - 820/826 companies successfully enriched (99.3% completion)
    - 538 companies web-scraped for HEI verification
    - Dual-model validation (Claude + GPT-4o) for all records
    """)

# ── PAGE 2: AI Agent Chat ─────────────────────────────────────────────────────
elif page == "💬 AI Agent Chat":
    st.title("💬 AI Agent Chat")
    st.markdown("Ask questions in natural language about the company database")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.markdown("**Example queries:**")
    examples = [
        "Show me all EdTech companies",
        "Which companies have university partners?",
        "List companies in California",
        "Find Series A funded companies",
        "Companies founded after 2020"
    ]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        if cols[i].button(example, key=f"example_{i}"):
            st.session_state.user_query = example
    
    user_query = st.text_input("Your question:", key="query_input", value=st.session_state.get('user_query', ''))
    
    if st.button("🔍 Search") and user_query:
        with st.spinner("Generating SQL and querying database..."):
            sql = generate_sql(user_query)
            st.code(sql, language="sql")
            
            results_df, error = execute_query(sql)
            
            if error:
                st.error(f"❌ Error: {error}")
            elif results_df is not None and len(results_df) > 0:
                st.success(f"✅ Found {len(results_df)} results")
                st.dataframe(results_df, use_container_width=True)
                
                st.session_state.chat_history.append({
                    'query': user_query,
                    'sql': sql,
                    'results': len(results_df)
                })
            else:
                st.warning("No results found")
    
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### Recent Queries")
        for i, item in enumerate(reversed(st.session_state.chat_history[-5:])):
            with st.expander(f"{item['query']} ({item['results']} results)"):
                st.code(item['sql'], language="sql")

# ── PAGE 3: Company Lookup with Benchmarking ──────────────────────────────────
elif page == "🔎 Company Lookup":
    st.title("🔎 Company Lookup & Competitive Benchmarking")
    
    company_name = st.selectbox("Select a company", [""] + get_company_names())
    
    if company_name:
        company = get_company_details(company_name)
        
        if company is not None:
            st.markdown(f"## {company_name}")
            
            # Company details
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
            
            # Description
            st.markdown("### Description")
            st.write(company['claude_description'] or "No description available")
            
            # HEI Institutions
            if company['claude_hei_found'] == 'Yes' and company['claude_hei_institutions']:
                st.markdown("### University/HEI Partners")
                st.info(company['claude_hei_institutions'])
            
            st.markdown("---")
            
            # === NEW: Industry Benchmarking ===
            st.markdown("### 📊 Industry Benchmarking")
            
            industry = company['claude_industry']
            benchmarks = get_industry_benchmarks(industry)
            
            if benchmarks:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Industry Peers", benchmarks['total_companies'])
                
                with col2:
                    company_has_hei = "Yes" if company['claude_hei_found'] == 'Yes' else "No"
                    st.metric("HEI Penetration (Industry Avg)", 
                             f"{benchmarks['hei_penetration']}%",
                             delta=f"This company: {company_has_hei}")
                
                with col3:
                    st.metric("Common Funding Stage", benchmarks['common_funding_stage'])
                
                with col4:
                    st.metric("Typical Company Size", benchmarks['typical_size'])
                
                # Competitive positioning
                st.markdown("#### Competitive Positioning")
                
                has_hei = company['claude_hei_found'] == 'Yes'
                industry_avg = benchmarks['hei_penetration']
                
                if has_hei and industry_avg < 50:
                    st.success(f"✅ **Competitive Advantage**: This company has HEI partners while only {industry_avg}% of {industry} companies do")
                elif not has_hei and industry_avg > 50:
                    st.warning(f"⚠️ **Opportunity Gap**: {industry_avg}% of {industry} companies have HEI partners, but this one doesn't")
                elif has_hei:
                    st.info(f"✓ **On Par**: Has HEI partners like {industry_avg}% of industry peers")
                else:
                    st.info(f"→ **Standard**: No HEI partners (industry avg: {industry_avg}%)")
            
            st.markdown("---")
            
            # Model Agreement
            st.markdown("### Model Agreement")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Industry Match", company['industry_agreement'] or "Unknown")
            with col2:
                st.metric("Location Match", company['location_agreement'] or "Unknown")
            with col3:
                st.metric("Confidence Level", company['confidence_level'] or "Unknown")
            
            # Competitors
            st.markdown("---")
            st.markdown("### Similar Companies / Potential Competitors")
            
            competitors = find_competitors(company_name)
            
            if len(competitors) > 0:
                st.dataframe(competitors, use_container_width=True)
                
                # Competitive summary
                total_competitors = len(competitors)
                competitors_with_hei = (competitors['claude_hei_found'] == 'Yes').sum()
                
                st.markdown("#### Competitive Landscape Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Similar Companies Found", total_competitors)
                with col2:
                    st.metric("Competitors with HEI Partners", 
                             f"{competitors_with_hei} ({competitors_with_hei/total_competitors*100:.0f}%)")
            else:
                st.info("No similar companies found in database")

# ── PAGE 4: Company Divergence Analysis ──────────────────────────────────────
elif page == "🎯 Company Divergence":
    st.title("🎯 Company Divergence Analysis")
    st.markdown("Identifying outlier companies that don't fit standard patterns")
    
    df = load_data()
    df_complete = df[df['claude_status'] == 'done'].copy()
    
    # Summary metrics
    st.markdown("### 📊 Divergence Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Funding/Size Anomalies", "57")
    with col2:
        st.metric("Industry Outliers", "5")
    with col3:
        st.metric("HEI Divergence", "10")
    with col4:
        st.metric("Multi-Dimensional", "3")
    
    st.markdown("---")
    
    # Tab interface for different divergence types
    tab1, tab2, tab3 = st.tabs(["💰 Funding/Size Anomalies", "📏 Industry Outliers", "🎓 HEI Divergence"])
    
    with tab1:
        st.markdown("### Companies with Unusual Funding/Size Combinations")
        
        # Calculate funding/size anomalies
        def extract_size_midpoint(size_range):
            if pd.isna(size_range) or size_range == "Unknown":
                return None
            mapping = {"1-10": 5, "11-50": 30, "51-200": 125, "201-500": 350, "500+": 750}
            return mapping.get(size_range)
        
        def extract_funding_order(stage):
            if pd.isna(stage) or stage == "Unknown":
                return None
            order = {"Bootstrapped": 0, "Seed": 1, "Series A": 2, "Series B": 3, "Series C": 4, "Public": 5}
            return order.get(stage)
        
        df_complete['size_numeric'] = df_complete['claude_company_size'].apply(extract_size_midpoint)
        df_complete['funding_numeric'] = df_complete['claude_funding_stage'].apply(extract_funding_order)
        
        # Find anomalies
        anomalies = []
        for _, company in df_complete.iterrows():
            size = company['size_numeric']
            funding = company['funding_numeric']
            
            if pd.isna(size) or pd.isna(funding):
                continue
            
            # Small team + late stage funding
            if size <= 30 and funding >= 3:
                anomalies.append({
                    'Company': company['company_name'],
                    'Industry': company['claude_industry'],
                    'Size': company['claude_company_size'],
                    'Funding': company['claude_funding_stage'],
                    'Anomaly Type': '🔴 Late-stage funding with small team'
                })
            
            # Large team + early stage
            if size >= 350 and funding <= 1:
                anomalies.append({
                    'Company': company['company_name'],
                    'Industry': company['claude_industry'],
                    'Size': company['claude_company_size'],
                    'Funding': company['claude_funding_stage'],
                    'Anomaly Type': '🟡 Large team with minimal funding'
                })
        
        if anomalies:
            anomalies_df = pd.DataFrame(anomalies)
            st.dataframe(anomalies_df, use_container_width=True)
            
            st.markdown("#### Insight")
            st.info(f"""
            Found **{len(anomalies)} companies** with unusual patterns:
            - Companies with Series B+ funding but <50 employees may be capital-intensive or acquisition targets
            - Companies with 200+ employees but Seed/Bootstrapped may be profitable lifestyle businesses
            """)
        else:
            st.warning("No funding/size anomalies detected")
    
    with tab2:
        st.markdown("### Industry Size Outliers")
        st.markdown("Companies significantly larger or smaller than their industry peers")
        
        # Calculate z-scores by industry
        from scipy import stats
        
        outliers = []
        for industry in df_complete['claude_industry'].value_counts().head(15).index:
            industry_df = df_complete[df_complete['claude_industry'] == industry].copy()
            
            if len(industry_df) < 5:
                continue
            
            valid_sizes = industry_df['size_numeric'].dropna()
            if len(valid_sizes) < 3:
                continue
            
            industry_df.loc[industry_df['size_numeric'].notna(), 'size_zscore'] = stats.zscore(valid_sizes)
            
            outlier_companies = industry_df[abs(industry_df['size_zscore']) > 2]
            
            for _, company in outlier_companies.iterrows():
                outliers.append({
                    'Company': company['company_name'],
                    'Industry': industry,
                    'Size': company['claude_company_size'],
                    'Deviation': 'Much larger than peers' if company['size_zscore'] > 0 else 'Much smaller than peers',
                    'Z-Score': f"{company['size_zscore']:.2f}"
                })
        
        if outliers:
            outliers_df = pd.DataFrame(outliers)
            st.dataframe(outliers_df, use_container_width=True)
            
            st.markdown("#### Insight")
            st.info(f"Identified **{len(outliers)} companies** that are statistical outliers (>2 standard deviations) from their industry peer group in terms of company size.")
        else:
            st.warning("No significant industry outliers detected")
    
    with tab3:
        st.markdown("### HEI Partnership Divergence")
        st.markdown("Companies breaking industry norms for university partnerships")
        
        # Calculate HEI penetration by industry
        industry_hei_rates = df_complete.groupby('claude_industry').apply(
            lambda x: (x['claude_hei_found'] == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0
        ).to_dict()
        
        hei_divergent = []
        
        for _, company in df_complete.iterrows():
            industry = company['claude_industry']
            has_hei = company['claude_hei_found'] == 'Yes'
            
            if industry not in industry_hei_rates:
                continue
            
            industry_rate = industry_hei_rates[industry]
            
            # Has HEI when rare in industry
            if has_hei and industry_rate < 20:
                hei_divergent.append({
                    'Company': company['company_name'],
                    'Industry': industry,
                    'HEI Partners': 'Yes',
                    'Industry Avg': f"{industry_rate:.0f}%",
                    'Pattern': '🟢 Engaging universities in non-traditional sector'
                })
            
            # Missing HEI when common in industry
            if not has_hei and industry_rate > 60:
                hei_divergent.append({
                    'Company': company['company_name'],
                    'Industry': industry,
                    'HEI Partners': 'No',
                    'Industry Avg': f"{industry_rate:.0f}%",
                    'Pattern': '🔴 Missing partnerships common in sector'
                })
        
        if hei_divergent:
            hei_df = pd.DataFrame(hei_divergent)
            st.dataframe(hei_df, use_container_width=True)
            
            st.markdown("#### Insight")
            st.info(f"""
            Found **{len(hei_divergent)} companies** with unexpected HEI patterns:
            - Companies with HEI partners in industries where it's rare may be innovators
            - Companies without HEI partners in industries where it's common may have missed opportunities
            """)
        else:
            st.warning("No significant HEI divergence detected")

# ── PAGE 5: Market Opportunity Analysis ───────────────────────────────────────
elif page == "📈 Market Opportunity":
    st.title("📈 Market Opportunity Analysis")
    st.markdown("Identify underserved markets with high growth potential")
    
    opportunities = identify_market_opportunities()
    
    # Top opportunities table
    st.markdown("### 🎯 Top Market Opportunities")
    st.markdown("**High company count + Low HEI penetration = Untapped market**")
    
    top_10 = opportunities.head(10)[['Industry', 'Total_Companies', 'HEI_Partners', 'Penetration_Rate', 'Opportunity_Score']]
    st.dataframe(top_10, use_container_width=True)
    
    st.markdown("---")
    
    # Opportunity Matrix
    st.markdown("### 📊 Market Opportunity Matrix")
    
    fig = px.scatter(
        opportunities,
        x='Penetration_Rate',
        y='Total_Companies',
        size='Opportunity_Score',
        color='Opportunity_Score',
        hover_data=['Industry'],
        labels={
            'Penetration_Rate': 'HEI Penetration Rate (%)',
            'Total_Companies': 'Market Size (Number of Companies)',
            'Opportunity_Score': 'Opportunity Score'
        },
        title='Market Opportunity Quadrants',
        color_continuous_scale='RdYlGn_r'
    )
    
    fig.add_hline(y=opportunities['Total_Companies'].median(), line_dash="dash", line_color="gray")
    fig.add_vline(x=opportunities['Penetration_Rate'].median(), line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Quadrant Interpretation:**
    - **Top Left (Low Penetration + Large Market)**: 🎯 **Prime Opportunity** — Many companies, few HEI partnerships
    - **Top Right (High Penetration + Large Market)**: Saturated market
    - **Bottom Left (Low Penetration + Small Market)**: Niche opportunity
    - **Bottom Right (High Penetration + Small Market)**: Limited opportunity
    """)
    
    st.markdown("---")
    
    # Industry Deep Dive
    st.markdown("### 🔍 Industry Deep Dive")
    selected_industry = st.selectbox("Select an industry for detailed analysis", opportunities['Industry'].tolist())
    
    if selected_industry:
        industry_data = opportunities[opportunities['Industry'] == selected_industry].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Companies", int(industry_data['Total_Companies']))
        with col2:
            st.metric("Companies with HEI Partners", int(industry_data['HEI_Partners']))
        with col3:
            st.metric("Penetration Rate", f"{industry_data['Penetration_Rate']}%")
        
        st.markdown(f"**Opportunity Score: {industry_data['Opportunity_Score']}/100**")
        
        # Get companies in this industry
        df = load_data()
        industry_companies = df[df['claude_industry'] == selected_industry][['company_name', 'claude_hei_found', 'claude_funding_stage', 'claude_location']]
        
        st.markdown(f"#### Companies in {selected_industry}")
        st.dataframe(industry_companies, use_container_width=True)

# ── PAGE 5: KPI Dashboard ─────────────────────────────────────────────────────
elif page == "📊 KPI Dashboard":
    st.title("📊 Business KPI Dashboard")
    st.markdown("Key performance indicators and metrics")
    
    df = load_data()
    df_complete = df[df['claude_status'] == 'done'].copy()
    
    # Top-level KPIs
    st.markdown("### Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_enriched = len(df_complete)
        st.metric("Enriched Companies", total_enriched, 
                 delta=f"{total_enriched/826*100:.1f}% of total")
    
    with col2:
        hei_count = (df_complete['claude_hei_found'] == 'Yes').sum()
        st.metric("HEI Partnerships", hei_count,
                 delta=f"{hei_count/total_enriched*100:.1f}% penetration")
    
    with col3:
        concentration = calculate_market_concentration()
        st.metric("Top 5 Industry Concentration", 
                 f"{concentration['top_5_concentration']}%")
    
    with col4:
        unique_industries = df_complete['claude_industry'].nunique()
        st.metric("Unique Industries", unique_industries)
    
    st.markdown("---")
    
    # HEI Penetration by Industry
    st.markdown("### 📈 HEI Penetration Rate by Industry (Top 15)")
    
    penetration_data = calculate_hei_penetration().head(15)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=penetration_data['Penetration_Rate'],
        y=penetration_data['Industry'],
        orientation='h',
        marker_color=penetration_data['Penetration_Rate'],
        marker_colorscale='RdYlGn',
        text=penetration_data['Penetration_Rate'].apply(lambda x: f"{x}%"),
        textposition='outside'
    ))
    
    fig.update_layout(
        xaxis_title="HEI Penetration Rate (%)",
        yaxis_title="Industry",
        height=600,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Geographic Distribution
    st.markdown("### 🌍 Geographic Distribution Index")
    
    def extract_country(loc):
        if pd.isna(loc) or loc == "Unknown":
            return "Unknown"
        parts = str(loc).split(',')
        return parts[-1].strip() if len(parts) >= 2 else str(loc)
    
    df_complete['country'] = df_complete['claude_location'].apply(extract_country)
    geo_dist = df_complete['country'].value_counts().head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(values=geo_dist.values, names=geo_dist.index, 
                    title="Top 10 Countries by Company Count", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(x=geo_dist.values, y=geo_dist.index, orientation='h',
                    labels={'x': 'Number of Companies', 'y': 'Country'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Data Quality Metrics
    st.markdown("---")
    st.markdown("### ✅ Data Quality Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_conf = (df_complete['confidence_level'] == 'High').sum()
        st.metric("High Confidence Records", high_conf,
                 delta=f"{high_conf/len(df_complete)*100:.1f}%")
    
    with col2:
        both_models = ((df_complete['claude_status'] == 'done') & 
                      (df_complete['gpt_status'] == 'done')).sum()
        st.metric("Dual-Model Validation", both_models,
                 delta=f"{both_models/len(df_complete)*100:.1f}%")
    
    with col3:
        scraped = (df_complete['scrape_status'] == 'done').sum()
        st.metric("Web Scrape Completion", scraped,
                 delta=f"{scraped/len(df_complete)*100:.1f}%")

# ── PAGE 6: Visual Analytics ──────────────────────────────────────────────────
elif page == "📉 Visual Analytics":
    st.title("📉 Visual Analytics Dashboard")
    
    df = load_data()
    df_complete = df[(df['claude_status'] == 'done') & (df['gpt_status'] == 'done')].copy()
    
    # Top Industries
    st.markdown("### Top 10 Industries")
    top_industries = df_complete['claude_industry'].value_counts().head(10)
    fig = px.bar(x=top_industries.values, y=top_industries.index, orientation='h',
                 labels={'x': 'Count', 'y': 'Industry'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Geographic Distribution
    st.markdown("### Geographic Distribution")
    def extract_country(loc):
        if pd.isna(loc) or loc == "Unknown":
            return "Unknown"
        parts = str(loc).split(',')
        return parts[-1].strip() if len(parts) >= 2 else str(loc)
    
    df_complete['country'] = df_complete['claude_location'].apply(extract_country)
    top_countries = df_complete['country'].value_counts().head(10)
    fig = px.pie(values=top_countries.values, names=top_countries.index, hole=0.3)
    st.plotly_chart(fig, use_container_width=True)
    
    # Funding Stage
    st.markdown("### Funding Stage Distribution")
    funding = df_complete['claude_funding_stage'].value_counts()
    fig = px.bar(x=funding.index, y=funding.values, labels={'x': 'Stage', 'y': 'Count'})
    st.plotly_chart(fig, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("**Independent Study Project**")
st.sidebar.markdown("MS Business Analytics - AI Specialization")
st.sidebar.markdown("Worcester Polytechnic Institute")
