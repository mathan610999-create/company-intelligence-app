"""
Company Intelligence Enrichment Pipeline v2
- Reads 826 companies from Excel
- Enriches each using Claude + GPT-4o independently
- Scrapes each company website for HEI partner mentions
- Stores all outputs side by side in SQLite + exports to Excel
- Resumes automatically if interrupted
"""

import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from tqdm import tqdm
import anthropic
from openai import OpenAI

# ── API Keys (set as environment variables before running) ────────────────────
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

if not CLAUDE_API_KEY or not OPENAI_API_KEY:
    raise ValueError(
        "Missing API keys. Please set them before running:\n"
        "  set CLAUDE_API_KEY=your_key_here\n"
        "  set OPENAI_API_KEY=your_key_here"
    )

claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ── Config ────────────────────────────────────────────────────────────────────
DB_PATH      = "company_intelligence.db"
EXCEL_INPUT  = "List of companies not in PB.xlsx"
EXCEL_OUTPUT = "company_intelligence_output.xlsx"

# ── Database setup ────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name             TEXT UNIQUE,

            -- Claude outputs
            claude_website           TEXT,
            claude_industry          TEXT,
            claude_location          TEXT,
            claude_founded_year      TEXT,
            claude_company_size      TEXT,
            claude_funding_stage     TEXT,
            claude_description       TEXT,
            claude_hei_found         TEXT,
            claude_hei_institutions  TEXT,
            claude_status            TEXT DEFAULT 'pending',

            -- GPT-4o outputs
            gpt_website              TEXT,
            gpt_industry             TEXT,
            gpt_location             TEXT,
            gpt_founded_year         TEXT,
            gpt_company_size         TEXT,
            gpt_funding_stage        TEXT,
            gpt_description          TEXT,
            gpt_hei_found            TEXT,
            gpt_hei_institutions     TEXT,
            gpt_status               TEXT DEFAULT 'pending',

            -- Web scraping outputs
            scraped_website          TEXT,
            scraped_hei_found        TEXT,
            scraped_hei_institutions TEXT,
            scrape_status            TEXT DEFAULT 'pending',

            -- Agreement analysis
            industry_agreement       TEXT,
            location_agreement       TEXT,
            hei_agreement            TEXT,
            confidence_level         TEXT
        )
    """)
    conn.commit()
    conn.close()

# ── Prompt ────────────────────────────────────────────────────────────────────
def build_prompt(company_name):
    return f"""You are a business research analyst. Research the company "{company_name}" and return ONLY a valid JSON object with these exact fields. Use "Unknown" if you are not sure.

{{
  "website": "company website URL or Unknown",
  "industry": "primary industry or sector",
  "location": "city, state, country",
  "founded_year": "year founded or Unknown",
  "company_size": "employee count range: 1-10 / 11-50 / 51-200 / 201-500 / 500+ / Unknown",
  "funding_stage": "Bootstrapped / Seed / Series A / Series B / Series C / Public / Unknown",
  "description": "2-3 sentence description of what the company does",
  "hei_found": "Yes or No - do they list any universities or higher education institutions as clients, partners or customers",
  "hei_institutions": "comma separated list of named universities or HEIs, or None"
}}

Return ONLY the JSON object. No explanation, no markdown, no extra text."""

# ── Claude enrichment ─────────────────────────────────────────────────────────
def enrich_with_claude(company_name):
    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": build_prompt(company_name)}]
        )
        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text), "done"
    except json.JSONDecodeError as e:
        print(f"  Claude JSON parse error for {company_name}: {e}")
        return None, "error"
    except Exception as e:
        print(f"  Claude API error for {company_name}: {e}")
        return None, "error"

# ── GPT-4o enrichment ─────────────────────────────────────────────────────────
def enrich_with_gpt(company_name):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1000,
            messages=[{"role": "user", "content": build_prompt(company_name)}]
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text), "done"
    except json.JSONDecodeError as e:
        print(f"  GPT JSON parse error for {company_name}: {e}")
        return None, "error"
    except Exception as e:
        print(f"  GPT API error for {company_name}: {e}")
        return None, "error"

# ── Web scraper for HEI mentions ──────────────────────────────────────────────
HEI_KEYWORDS = [
    "university", "college", "institute of technology",
    "community college", "polytechnic", "higher education",
    "school of business", "school of engineering", "school of education"
]

def scrape_hei(website_url):
    if not website_url or website_url.lower() == "unknown":
        return "Unknown", "None", "skipped"
    try:
        if not website_url.startswith("http"):
            website_url = "https://" + website_url
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(website_url, timeout=10, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ").lower()

        found = []
        for keyword in HEI_KEYWORDS:
            if keyword in text:
                idx = text.find(keyword)
                snippet = text[max(0, idx - 20):idx + 60].strip()
                found.append(snippet)

        if found:
            return "Yes", "; ".join(set(found[:5])), "done"
        return "No", "None", "done"
    except Exception as e:
        return "Error", str(e)[:100], "error"

# ── Agreement analysis ────────────────────────────────────────────────────────
def calculate_agreement(claude_data, gpt_data):
    if not claude_data or not gpt_data:
        return "Unknown", "Unknown", "Unknown", "Low"

    def normalize(val):
        return str(val).lower().strip() if val else ""

    industry_match = "Yes" if normalize(claude_data.get("industry")) == normalize(gpt_data.get("industry")) else "No"
    location_match  = "Yes" if normalize(claude_data.get("location")) == normalize(gpt_data.get("location")) else "No"
    hei_match       = "Yes" if normalize(claude_data.get("hei_found")) == normalize(gpt_data.get("hei_found")) else "No"

    matches     = [industry_match, location_match, hei_match].count("Yes")
    confidence  = "High" if matches == 3 else "Medium" if matches >= 2 else "Low"

    return industry_match, location_match, hei_match, confidence

# ── Upsert helper ─────────────────────────────────────────────────────────────
def upsert_company(c, company_name):
    c.execute("SELECT id FROM companies WHERE company_name=?", (company_name,))
    if not c.fetchone():
        c.execute("INSERT INTO companies (company_name) VALUES (?)", (company_name,))

# ── Main pipeline ─────────────────────────────────────────────────────────────
def run_pipeline(limit=None):
    init_db()

    df       = pd.read_excel(EXCEL_INPUT)
    companies = df["Company"].tolist()
    if limit:
        companies = companies[:limit]

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    for company in tqdm(companies, desc="Processing"):
        upsert_company(c, company)
        conn.commit()

        # Fetch current row status
        c.execute("""
            SELECT claude_status, gpt_status, scrape_status
            FROM companies WHERE company_name=?
        """, (company,))
        row = c.fetchone()
        claude_done, gpt_done, scrape_done = row if row else ("pending", "pending", "pending")

        claude_data = None
        gpt_data    = None

        # ── Claude enrichment (skip if already done) ──
        if claude_done != "done":
            print(f"\n[Claude] {company}")
            claude_data, claude_status = enrich_with_claude(company)
            time.sleep(0.5)
            if claude_data:
                c.execute("""
                    UPDATE companies SET
                        claude_website=?, claude_industry=?, claude_location=?,
                        claude_founded_year=?, claude_company_size=?, claude_funding_stage=?,
                        claude_description=?, claude_hei_found=?, claude_hei_institutions=?,
                        claude_status=?
                    WHERE company_name=?
                """, (
                    claude_data.get("website"), claude_data.get("industry"),
                    claude_data.get("location"), claude_data.get("founded_year"),
                    claude_data.get("company_size"), claude_data.get("funding_stage"),
                    claude_data.get("description"), claude_data.get("hei_found"),
                    claude_data.get("hei_institutions"), claude_status, company
                ))
                conn.commit()
        else:
            # Load existing claude data for agreement calc
            c.execute("""
                SELECT claude_website, claude_industry, claude_location,
                       claude_founded_year, claude_company_size, claude_funding_stage,
                       claude_description, claude_hei_found, claude_hei_institutions
                FROM companies WHERE company_name=?
            """, (company,))
            r = c.fetchone()
            if r:
                keys = ["website","industry","location","founded_year","company_size","funding_stage","description","hei_found","hei_institutions"]
                claude_data = dict(zip(keys, r))

        # ── GPT enrichment (skip if already done) ──
        if gpt_done != "done":
            print(f"[GPT]    {company}")
            gpt_data, gpt_status = enrich_with_gpt(company)
            time.sleep(0.5)
            if gpt_data:
                c.execute("""
                    UPDATE companies SET
                        gpt_website=?, gpt_industry=?, gpt_location=?,
                        gpt_founded_year=?, gpt_company_size=?, gpt_funding_stage=?,
                        gpt_description=?, gpt_hei_found=?, gpt_hei_institutions=?,
                        gpt_status=?
                    WHERE company_name=?
                """, (
                    gpt_data.get("website"), gpt_data.get("industry"),
                    gpt_data.get("location"), gpt_data.get("founded_year"),
                    gpt_data.get("company_size"), gpt_data.get("funding_stage"),
                    gpt_data.get("description"), gpt_data.get("hei_found"),
                    gpt_data.get("hei_institutions"), gpt_status, company
                ))
                conn.commit()
        else:
            c.execute("""
                SELECT gpt_website, gpt_industry, gpt_location,
                       gpt_founded_year, gpt_company_size, gpt_funding_stage,
                       gpt_description, gpt_hei_found, gpt_hei_institutions
                FROM companies WHERE company_name=?
            """, (company,))
            r = c.fetchone()
            if r:
                keys = ["website","industry","location","founded_year","company_size","funding_stage","description","hei_found","hei_institutions"]
                gpt_data = dict(zip(keys, r))

        # ── Web scraping (skip if already done) ──
        if scrape_done != "done":
            website = claude_data.get("website") if claude_data else None
            scraped_hei, scraped_inst, scrape_status = scrape_hei(website)
            c.execute("""
                UPDATE companies SET
                    scraped_website=?, scraped_hei_found=?,
                    scraped_hei_institutions=?, scrape_status=?
                WHERE company_name=?
            """, (website, scraped_hei, scraped_inst, scrape_status, company))
            conn.commit()

        # ── Agreement analysis (always recalculate) ──
        ind_agree, loc_agree, hei_agree, confidence = calculate_agreement(claude_data, gpt_data)
        c.execute("""
            UPDATE companies SET
                industry_agreement=?, location_agreement=?,
                hei_agreement=?, confidence_level=?
            WHERE company_name=?
        """, (ind_agree, loc_agree, hei_agree, confidence, company))
        conn.commit()

    conn.close()
    print("\nPipeline complete!")
    export_to_excel()

# ── Export to Excel ───────────────────────────────────────────────────────────
def export_to_excel():
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM companies", conn)
    conn.close()
    df.to_excel(EXCEL_OUTPUT, index=False)
    print(f"Exported to {EXCEL_OUTPUT}")

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_pipeline(
        limit=None  # Change to None to run all 826
    )