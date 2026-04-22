"""
Company Intelligence AI Agent
Natural language interface to query the enriched company database
Uses LangChain + Claude API for query understanding and SQL generation
"""

import sqlite3
import os
from anthropic import Anthropic

# ── Config ────────────────────────────────────────────────────────────────────
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
if not CLAUDE_API_KEY:
    raise ValueError("Please set CLAUDE_API_KEY environment variable")

client = Anthropic(api_key=CLAUDE_API_KEY)
DB_PATH = "company_intelligence.db"

# ── Database schema ───────────────────────────────────────────────────────────
SCHEMA = """
Database Schema:

Table: companies
Columns:
  - company_name (TEXT): Company name
  - claude_industry (TEXT): Industry/sector from Claude
  - claude_location (TEXT): Location (city, state, country)
  - claude_founded_year (TEXT): Year founded
  - claude_company_size (TEXT): Employee count range (1-10, 11-50, 51-200, 201-500, 500+)
  - claude_funding_stage (TEXT): Funding stage (Bootstrapped, Seed, Series A, Series B, Series C, Public)
  - claude_description (TEXT): Company description
  - claude_hei_found (TEXT): Whether HEI partners found (Yes/No)
  - claude_hei_institutions (TEXT): Named HEI partners
  - gpt_industry (TEXT): Industry from GPT
  - gpt_location (TEXT): Location from GPT
  - gpt_hei_found (TEXT): HEI partners from GPT
  - confidence_level (TEXT): Agreement confidence (High/Medium/Low)

Note: Use Claude columns as primary source. GPT columns available for comparison.
"""

# ── Query Agent ───────────────────────────────────────────────────────────────
def generate_sql(user_query):
    """Convert natural language query to SQL using Claude"""
    prompt = f"""You are a SQL expert. Convert the following natural language query into a valid SQLite query.

{SCHEMA}

User Query: {user_query}

Rules:
1. Use claude_* columns as primary data source
2. Return ONLY the SQL query, nothing else
3. Always include company_name in SELECT
4. Use LIKE for text matching (case-insensitive with LOWER())
5. Limit results to 50 unless user asks for more
6. For "all" queries, don't add unnecessary WHERE clauses

Examples:
- "Show me EdTech companies" → SELECT company_name, claude_industry FROM companies WHERE LOWER(claude_industry) LIKE '%edtech%' OR LOWER(claude_industry) LIKE '%education%technology%' LIMIT 50
- "Companies with HEI partners" → SELECT company_name, claude_hei_institutions FROM companies WHERE claude_hei_found = 'Yes' LIMIT 50
- "California companies" → SELECT company_name, claude_location FROM companies WHERE LOWER(claude_location) LIKE '%california%' LIMIT 50

Now generate SQL for: {user_query}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    sql = response.content[0].text.strip()
    # Clean markdown fences if present
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def execute_query(sql):
    """Execute SQL and return results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return results, columns
    except Exception as e:
        conn.close()
        raise Exception(f"SQL execution error: {e}")

def format_results(results, columns):
    """Format results as readable text"""
    if not results:
        return "No results found."
    
    # Create header
    header = " | ".join(columns)
    separator = "-" * len(header)
    
    # Format rows
    rows = []
    for row in results[:50]:  # Limit display to 50
        rows.append(" | ".join(str(val) if val else "N/A" for val in row))
    
    output = f"{header}\n{separator}\n" + "\n".join(rows)
    
    if len(results) > 50:
        output += f"\n\n(Showing first 50 of {len(results)} results)"
    
    return output

def chat(user_query):
    """Main agent function"""
    print(f"\n🔍 Query: {user_query}\n")
    
    # Generate SQL
    print("Generating SQL...")
    sql = generate_sql(user_query)
    print(f"SQL: {sql}\n")
    
    # Execute
    try:
        results, columns = execute_query(sql)
        output = format_results(results, columns)
        print(output)
        print(f"\n✅ Found {len(results)} results")
        return results, columns
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

# ── Interactive mode ──────────────────────────────────────────────────────────
def interactive_mode():
    """Run interactive chat loop"""
    print("=" * 80)
    print("Company Intelligence AI Agent")
    print("=" * 80)
    print("\nAsk questions in natural language. Type 'exit' to quit.\n")
    print("Example queries:")
    print("  - Show me all EdTech companies")
    print("  - Which companies have HEI partners?")
    print("  - List companies in California")
    print("  - Find Series A funded companies")
    print("  - Companies founded after 2015")
    print()
    
    while True:
        user_input = input("Query: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        chat(user_input)
        print()

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # You can either run interactive mode or call chat() directly
    
    # Interactive mode
    interactive_mode()
    
    # OR single query mode (uncomment to use)
    # chat("Show me all companies with HEI partners")
