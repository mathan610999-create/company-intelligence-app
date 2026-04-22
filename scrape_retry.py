"""
Scrape Retry Script
- Retries 66 errored scrapes with better timeout handling
- For 246 skipped companies (no website found), asks GPT to find the website first then scrapes
- Updates existing SQLite database in place
- Exports updated Excel at the end
"""

import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
from tqdm import tqdm
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable before running.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

DB_PATH      = r"d:\Traavel_itenary\company_intelligence.db"
EXCEL_OUTPUT = "company_intelligence_output_v2.xlsx"

# ── HEI keywords ──────────────────────────────────────────────────────────────
HEI_KEYWORDS = [
    "university", "college", "institute of technology",
    "community college", "polytechnic", "higher education",
    "school of business", "school of engineering", "school of education"
]

# ── Ask GPT to find website ───────────────────────────────────────────────────
def find_website_with_gpt(company_name):
    try:
        prompt = f"""What is the official website URL for the company "{company_name}"? 
Return ONLY the URL, nothing else. If you don't know, return "Unknown"."""
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        url = response.choices[0].message.content.strip()
        url = url.replace("```", "").strip()
        if url.lower() == "unknown" or not ("." in url):
            return "Unknown"
        return url
    except Exception as e:
        print(f"  GPT website lookup error for {company_name}: {e}")
        return "Unknown"

# ── Web scraper with better timeout handling ──────────────────────────────────
def scrape_hei(website_url, company_name=""):
    if not website_url or website_url.lower() == "unknown":
        return "Unknown", "None", "skipped"
    try:
        if not website_url.startswith("http"):
            website_url = "https://" + website_url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        resp = requests.get(
            website_url,
            timeout=15,
            headers=headers,
            allow_redirects=True,
            verify=False  # Skip SSL verification for problematic sites
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

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

    except requests.exceptions.SSLError:
        # Retry without SSL verification already handled above
        return "Error", "SSL Error", "error"
    except requests.exceptions.ConnectionError:
        return "Error", "Connection Error", "error"
    except requests.exceptions.Timeout:
        return "Error", "Timeout", "error"
    except Exception as e:
        return "Error", str(e)[:100], "error"

# ── Main retry pipeline ───────────────────────────────────────────────────────
def run_retry():
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    # Get all companies that need retry
    c.execute("""
        SELECT company_name, claude_website, gpt_website, scrape_status
        FROM companies
        WHERE scrape_status IN ('error', 'skipped', 'pending')
    """)
    rows = c.fetchall()
    print(f"Found {len(rows)} companies to retry")

    # Separate into two groups
    skipped = [(r[0], r[1], r[2]) for r in rows if r[3] == 'skipped']
    errors  = [(r[0], r[1], r[2]) for r in rows if r[3] in ('error', 'pending')]

    print(f"  - Skipped (no website): {len(skipped)}")
    print(f"  - Errors (connection issues): {len(errors)}")

    # ── Step 1: Find websites for skipped companies ──
    print("\n=== Step 1: Finding websites for skipped companies ===")
    for company_name, claude_website, gpt_website in tqdm(skipped, desc="Finding websites"):
        # Try existing websites first
        website = None
        if claude_website and claude_website.lower() != "unknown":
            website = claude_website
        elif gpt_website and gpt_website.lower() != "unknown":
            website = gpt_website
        else:
            # Ask GPT to find it
            website = find_website_with_gpt(company_name)
            time.sleep(0.3)

        # Now scrape
        hei_found, hei_inst, status = scrape_hei(website, company_name)

        c.execute("""
            UPDATE companies SET
                scraped_website=?, scraped_hei_found=?,
                scraped_hei_institutions=?, scrape_status=?
            WHERE company_name=?
        """, (website, hei_found, hei_inst, status, company_name))
        conn.commit()

    # ── Step 2: Retry errored scrapes ──
    print("\n=== Step 2: Retrying errored scrapes ===")
    for company_name, claude_website, gpt_website in tqdm(errors, desc="Retrying errors"):
        website = claude_website or gpt_website or "Unknown"
        hei_found, hei_inst, status = scrape_hei(website, company_name)
        time.sleep(0.5)

        c.execute("""
            UPDATE companies SET
                scraped_hei_found=?, scraped_hei_institutions=?, scrape_status=?
            WHERE company_name=?
        """, (hei_found, hei_inst, status, company_name))
        conn.commit()

    conn.close()

    # ── Final summary ──
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM companies", conn)
    conn.close()

    print("\n=== Final Scrape Status ===")
    print(df['scrape_status'].value_counts().to_string())
    print(f"\nHEI found - Yes: {(df['scraped_hei_found'] == 'Yes').sum()}")
    print(f"HEI found - No:  {(df['scraped_hei_found'] == 'No').sum()}")

    df.to_excel(EXCEL_OUTPUT, index=False)
    print(f"\nExported to {EXCEL_OUTPUT}")

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    run_retry()
