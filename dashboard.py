"""
Company Intelligence Dashboard
Interactive visualizations of divergence analysis findings
Generates standalone HTML dashboard
"""

import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

DB_PATH = "company_intelligence.db"

# ── Load data ─────────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM companies", conn)
conn.close()

df_complete = df[(df['claude_status'] == 'done') & (df['gpt_status'] == 'done')].copy()

# ── Create dashboard ──────────────────────────────────────────────────────────
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        'Agreement Rates by Field',
        'Confidence Level Distribution',
        'HEI Detection Comparison',
        'Top 10 Industries (Claude)',
        'Geographic Distribution (Top 10 Locations)',
        'Funding Stage Distribution'
    ),
    specs=[
        [{"type": "bar"}, {"type": "pie"}],
        [{"type": "bar"}, {"type": "bar"}],
        [{"type": "bar"}, {"type": "bar"}]
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.15
)

# ── 1. Agreement Rates ────────────────────────────────────────────────────────
fields = ['Industry', 'Location', 'Founded Year', 'Company Size', 'Funding Stage', 'HEI Detection']
agreement_rates = [20.7, 51.1, 66.1, 65.9, 67.1, 52.8]

fig.add_trace(
    go.Bar(
        x=fields,
        y=agreement_rates,
        marker_color=['#e74c3c', '#f39c12', '#3498db', '#3498db', '#3498db', '#f39c12'],
        text=[f'{r}%' for r in agreement_rates],
        textposition='outside'
    ),
    row=1, col=1
)

# ── 2. Confidence Level Distribution ──────────────────────────────────────────
confidence_counts = df_complete['confidence_level'].value_counts()
fig.add_trace(
    go.Pie(
        labels=confidence_counts.index,
        values=confidence_counts.values,
        marker_colors=['#e74c3c', '#f39c12', '#2ecc71'],
        hole=0.3
    ),
    row=1, col=2
)

# ── 3. HEI Detection Comparison ───────────────────────────────────────────────
claude_hei = (df_complete['claude_hei_found'] == 'Yes').sum()
gpt_hei = (df_complete['gpt_hei_found'] == 'Yes').sum()
scraped_hei = (df_complete['scraped_hei_found'] == 'Yes').sum()

fig.add_trace(
    go.Bar(
        x=['Claude', 'GPT-4o', 'Web Scraped'],
        y=[claude_hei, gpt_hei, scraped_hei],
        marker_color=['#3498db', '#9b59b6', '#1abc9c'],
        text=[claude_hei, gpt_hei, scraped_hei],
        textposition='outside'
    ),
    row=2, col=1
)

# ── 4. Top 10 Industries ──────────────────────────────────────────────────────
top_industries = df_complete['claude_industry'].value_counts().head(10)
fig.add_trace(
    go.Bar(
        y=top_industries.index[::-1],
        x=top_industries.values[::-1],
        orientation='h',
        marker_color='#3498db',
        text=top_industries.values[::-1],
        textposition='outside'
    ),
    row=2, col=2
)

# ── 5. Geographic Distribution ────────────────────────────────────────────────
# Extract just the country/state from location
def extract_region(loc):
    if pd.isna(loc) or loc == "Unknown":
        return "Unknown"
    parts = str(loc).split(',')
    if len(parts) >= 2:
        return parts[-1].strip()  # Country
    return str(loc)

df_complete['region'] = df_complete['claude_location'].apply(extract_region)
top_regions = df_complete['region'].value_counts().head(10)

fig.add_trace(
    go.Bar(
        y=top_regions.index[::-1],
        x=top_regions.values[::-1],
        orientation='h',
        marker_color='#2ecc71',
        text=top_regions.values[::-1],
        textposition='outside'
    ),
    row=3, col=1
)

# ── 6. Funding Stage Distribution ─────────────────────────────────────────────
funding_stages = df_complete['claude_funding_stage'].value_counts().head(8)
fig.add_trace(
    go.Bar(
        x=funding_stages.index,
        y=funding_stages.values,
        marker_color='#9b59b6',
        text=funding_stages.values,
        textposition='outside'
    ),
    row=3, col=2
)

# ── Layout ────────────────────────────────────────────────────────────────────
fig.update_layout(
    title={
        'text': 'Company Intelligence Dashboard - Divergence Analysis Findings',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24, 'color': '#2c3e50'}
    },
    showlegend=False,
    height=1400,
    font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
    plot_bgcolor='white',
    paper_bgcolor='#ecf0f1'
)

# Update axes
fig.update_xaxes(showgrid=True, gridcolor='#bdc3c7')
fig.update_yaxes(showgrid=True, gridcolor='#bdc3c7')

# ── Add summary stats box ─────────────────────────────────────────────────────
summary_text = f"""
<b>Dataset Summary</b><br>
Total Companies: 826<br>
Enriched by Both Models: {len(df_complete)}<br>
High Confidence: {(df_complete['confidence_level'] == 'High').sum()}<br>
Overall Reliability: 53.9%
"""

fig.add_annotation(
    text=summary_text,
    xref="paper", yref="paper",
    x=0.98, y=0.98,
    showarrow=False,
    font=dict(size=12, color="#2c3e50"),
    bgcolor="#ecf0f1",
    bordercolor="#2c3e50",
    borderwidth=2,
    borderpad=10,
    align="left",
    xanchor="right",
    yanchor="top"
)

# ── Save dashboard ────────────────────────────────────────────────────────────
output_file = "company_intelligence_dashboard.html"
fig.write_html(output_file)
print(f"✅ Dashboard saved to: {output_file}")
print(f"   Open in browser to view interactive visualizations")

# Also create a simpler single-page summary
# ── Additional: Agreement Rate Detail ─────────────────────────────────────────
fig2 = go.Figure()

# Detailed agreement breakdown
categories = ['Industry', 'Location', 'Year', 'Size', 'Funding', 'HEI']
agree = [20.7, 51.1, 66.1, 65.9, 67.1, 52.8]
disagree = [100 - x for x in agree]

fig2.add_trace(go.Bar(
    name='Agree',
    x=categories,
    y=agree,
    marker_color='#2ecc71',
    text=[f'{x:.1f}%' for x in agree],
    textposition='inside'
))

fig2.add_trace(go.Bar(
    name='Disagree',
    x=categories,
    y=disagree,
    marker_color='#e74c3c',
    text=[f'{x:.1f}%' for x in disagree],
    textposition='inside'
))

fig2.update_layout(
    title='Inter-Model Agreement vs Disagreement by Field',
    barmode='stack',
    yaxis_title='Percentage',
    height=500,
    font=dict(size=14),
    plot_bgcolor='white'
)

fig2.write_html("agreement_breakdown.html")
print(f"✅ Agreement breakdown saved to: agreement_breakdown.html")
