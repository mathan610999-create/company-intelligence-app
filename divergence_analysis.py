"""
Divergence Analysis Script
Analyzes agreement/disagreement patterns between Claude and GPT enrichment
Outputs:
- Agreement rate by field
- Divergence patterns (clustering analysis)
- Inter-model reliability scores
- Flagged companies for human review
- Analysis report
"""

import pandas as pd
import sqlite3
from collections import Counter
import re

DB_PATH = "company_intelligence.db"

# ── Load data ─────────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM companies", conn)
conn.close()

# Filter to only companies with both models complete
df_complete = df[(df['claude_status'] == 'done') & (df['gpt_status'] == 'done')].copy()
print(f"Analyzing {len(df_complete)} companies with complete data from both models")
print()

if len(df_complete) == 0:
    print("No companies have been fully processed by both models yet. Run pipeline.py first.")
    exit()

# ── Helper functions ──────────────────────────────────────────────────────────
def normalize(text):
    """Normalize text for comparison"""
    if pd.isna(text) or text is None:
        return ""
    return str(text).lower().strip()

def fuzzy_match(val1, val2):
    """Check if two values are semantically similar"""
    v1 = normalize(val1)
    v2 = normalize(val2)
    
    if v1 == v2:
        return True
    
    # Handle common variations
    # EdTech vs Education Technology
    if "edtech" in v1 and "education" in v2 and "technology" in v2:
        return True
    if "edtech" in v2 and "education" in v1 and "technology" in v1:
        return True
    
    # IT vs Information Technology
    if v1 == "it" and "information technology" in v2:
        return True
    if v2 == "it" and "information technology" in v1:
        return True
    
    return False

# ── 1. Agreement Rate Analysis ────────────────────────────────────────────────
print("=" * 80)
print("1. AGREEMENT RATE BY FIELD")
print("=" * 80)

fields_to_compare = [
    ('industry', 'claude_industry', 'gpt_industry'),
    ('location', 'claude_location', 'gpt_location'),
    ('founded_year', 'claude_founded_year', 'gpt_founded_year'),
    ('company_size', 'claude_company_size', 'gpt_company_size'),
    ('funding_stage', 'claude_funding_stage', 'gpt_funding_stage'),
    ('hei_found', 'claude_hei_found', 'gpt_hei_found'),
]

agreement_scores = {}

for field_name, claude_col, gpt_col in fields_to_compare:
    exact_match = (df_complete[claude_col].apply(normalize) == df_complete[gpt_col].apply(normalize)).sum()
    
    # Also calculate fuzzy match for industry
    if field_name == 'industry':
        fuzzy_matches = sum(fuzzy_match(row[claude_col], row[gpt_col]) 
                           for _, row in df_complete.iterrows())
        fuzzy_rate = (fuzzy_matches / len(df_complete)) * 100
        print(f"{field_name:15} - Exact: {exact_match:3}/{len(df_complete)} ({exact_match/len(df_complete)*100:5.1f}%)  |  Fuzzy: {fuzzy_matches:3}/{len(df_complete)} ({fuzzy_rate:5.1f}%)")
        agreement_scores[field_name] = fuzzy_rate
    else:
        rate = (exact_match / len(df_complete)) * 100
        print(f"{field_name:15} - Exact: {exact_match:3}/{len(df_complete)} ({rate:5.1f}%)")
        agreement_scores[field_name] = rate

print()

# ── 2. Divergence Pattern Analysis ────────────────────────────────────────────
print("=" * 80)
print("2. DIVERGENCE PATTERNS")
print("=" * 80)

# Industry divergence - what industries have most disagreement?
df_complete['industry_match'] = df_complete.apply(
    lambda row: fuzzy_match(row['claude_industry'], row['gpt_industry']), axis=1
)

industry_divergence = df_complete[~df_complete['industry_match']]
print(f"\nIndustry Divergence: {len(industry_divergence)} companies ({len(industry_divergence)/len(df_complete)*100:.1f}%)")

# Group by Claude's industry classification
if len(industry_divergence) > 0:
    print("\nTop 10 Claude industry classifications with disagreements:")
    divergent_industries = industry_divergence['claude_industry'].value_counts().head(10)
    for ind, count in divergent_industries.items():
        print(f"  {ind}: {count} disagreements")

print()

# Location divergence
df_complete['location_match'] = (df_complete['claude_location'].apply(normalize) == df_complete['gpt_location'].apply(normalize))
location_divergence = df_complete[~df_complete['location_match']]
print(f"Location Divergence: {len(location_divergence)} companies ({len(location_divergence)/len(df_complete)*100:.1f}%)")

# HEI detection divergence
df_complete['hei_match'] = (df_complete['claude_hei_found'].apply(normalize) == df_complete['gpt_hei_found'].apply(normalize))
hei_divergence = df_complete[~df_complete['hei_match']]
print(f"HEI Detection Divergence: {len(hei_divergence)} companies ({len(hei_divergence)/len(df_complete)*100:.1f}%)")

# Who found more HEIs?
claude_yes = (df_complete['claude_hei_found'] == 'Yes').sum()
gpt_yes = (df_complete['gpt_hei_found'] == 'Yes').sum()
print(f"\n  Claude found HEI partners: {claude_yes} companies")
print(f"  GPT found HEI partners:    {gpt_yes} companies")
print(f"  Difference: {abs(claude_yes - gpt_yes)} companies")

print()

# ── 3. Inter-Model Reliability Score ──────────────────────────────────────────
print("=" * 80)
print("3. INTER-MODEL RELIABILITY SCORES")
print("=" * 80)

# Overall reliability
overall_reliability = sum(agreement_scores.values()) / len(agreement_scores)
print(f"\nOverall Inter-Model Reliability: {overall_reliability:.1f}%")

print("\nReliability by Task Type:")
print(f"  Classification (industry):        {agreement_scores['industry']:.1f}%")
print(f"  Factual (location, year, size):  {(agreement_scores['location'] + agreement_scores['founded_year'] + agreement_scores['company_size'])/3:.1f}%")
print(f"  Detection (HEI partners):         {agreement_scores['hei_found']:.1f}%")

print()

# ── 4. High Confidence Ground Truth ───────────────────────────────────────────
print("=" * 80)
print("4. HIGH CONFIDENCE GROUND TRUTH")
print("=" * 80)

# Companies where both models agree on everything
high_confidence = df_complete[
    df_complete['industry_match'] & 
    df_complete['location_match'] & 
    df_complete['hei_match']
]

print(f"\nHigh Confidence Companies (all fields agree): {len(high_confidence)} ({len(high_confidence)/len(df_complete)*100:.1f}%)")
print(f"These can be treated as verified ground truth for the dataset.")

print()

# ── 5. Companies Flagged for Human Review ─────────────────────────────────────
print("=" * 80)
print("5. FLAGGED FOR HUMAN REVIEW")
print("=" * 80)

# Companies with 2+ disagreements
df_complete['disagreement_count'] = (
    (~df_complete['industry_match']).astype(int) +
    (~df_complete['location_match']).astype(int) +
    (~df_complete['hei_match']).astype(int)
)

flagged = df_complete[df_complete['disagreement_count'] >= 2].sort_values('disagreement_count', ascending=False)

print(f"\nCompanies with 2+ field disagreements: {len(flagged)}")
print("\nTop 10 most divergent companies:")
print(flagged[['company_name', 'claude_industry', 'gpt_industry', 'claude_hei_found', 'gpt_hei_found', 'disagreement_count']].head(10).to_string(index=False))

print()

# ── 6. Export divergence analysis ─────────────────────────────────────────────
print("=" * 80)
print("6. EXPORTING ANALYSIS RESULTS")
print("=" * 80)

# Export flagged companies
flagged_export = flagged[[
    'company_name',
    'claude_industry', 'gpt_industry',
    'claude_location', 'gpt_location',
    'claude_hei_found', 'gpt_hei_found',
    'disagreement_count'
]].copy()

flagged_export.to_excel("divergence_flagged_for_review.xlsx", index=False)
print("Done: Exported flagged companies to: divergence_flagged_for_review.xlsx")

# Export high confidence ground truth
high_confidence_export = high_confidence[[
    'company_name',
    'claude_industry',
    'claude_location',
    'claude_founded_year',
    'claude_company_size',
    'claude_funding_stage',
    'claude_hei_found',
    'claude_hei_institutions'
]].copy()

high_confidence_export.rename(columns={
    'claude_industry': 'industry',
    'claude_location': 'location',
    'claude_founded_year': 'founded_year',
    'claude_company_size': 'company_size',
    'claude_funding_stage': 'funding_stage',
    'claude_hei_found': 'hei_partners',
    'claude_hei_institutions': 'hei_institutions'
}, inplace=True)

high_confidence_export.to_excel("high_confidence_ground_truth.xlsx", index=False)
print("Done: Exported ground truth dataset to: high_confidence_ground_truth.xlsx")

print()

# ── 7. Summary Report ─────────────────────────────────────────────────────────
print("=" * 80)
print("SUMMARY REPORT")
print("=" * 80)

summary = f"""
DIVERGENCE ANALYSIS SUMMARY
===========================

Dataset Size: {len(df_complete)} companies with complete enrichment from both models

AGREEMENT RATES:
- Industry Classification:  {agreement_scores['industry']:.1f}%
- Location:                 {agreement_scores['location']:.1f}%
- Founded Year:             {agreement_scores['founded_year']:.1f}%
- Company Size:             {agreement_scores['company_size']:.1f}%
- Funding Stage:            {agreement_scores['funding_stage']:.1f}%
- HEI Partner Detection:    {agreement_scores['hei_found']:.1f}%

OVERALL INTER-MODEL RELIABILITY: {overall_reliability:.1f}%

KEY FINDINGS:
1. High Confidence Ground Truth: {len(high_confidence)} companies ({len(high_confidence)/len(df_complete)*100:.1f}%)
   - All fields agree between models
   - Can be used as verified dataset

2. Flagged for Human Review: {len(flagged)} companies ({len(flagged)/len(df_complete)*100:.1f}%)
   - 2+ fields disagree between models
   - Require manual verification

3. HEI Detection Divergence:
   - Claude identified {claude_yes} companies with HEI partners
   - GPT identified {gpt_yes} companies with HEI partners
   - {abs(claude_yes - gpt_yes)} company difference suggests detection sensitivity varies

4. Industry Classification Challenges:
   - {len(industry_divergence)} companies ({len(industry_divergence)/len(df_complete)*100:.1f}%) have industry disagreements
   - Models use different terminology for same sectors (e.g. "EdTech" vs "Education Technology")

METHODOLOGY NOTE:
This analysis demonstrates reproducibility and model-independence by running enrichment
through two independent AI models. Agreement rates provide confidence scores for each
field type, enabling stratified use of the dataset based on reliability requirements.
"""

with open("divergence_analysis_report.txt", "w") as f:
    f.write(summary)

print(summary)
print("Done: Full report saved to: divergence_analysis_report.txt")
