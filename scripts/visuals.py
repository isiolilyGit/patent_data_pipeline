import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

BASE_DIR = Path(__file__).resolve().parent.parent

VIS_DIR = BASE_DIR / "visualizations"
VIS_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# Q1 TOP INVENTORS
# ─────────────────────────────────────────────

query = """
SELECT
    i.name,
    COUNT(pr.patent_id) AS patent_count

FROM inventors i

JOIN patent_relationships pr
    ON i.inventor_id = pr.inventor_id

GROUP BY i.name
ORDER BY patent_count DESC
LIMIT 10;
"""

df = pd.read_sql(query, engine)

plt.figure(figsize=(12, 6))

plt.bar(df["name"], df["patent_count"])

plt.xticks(rotation=45)

plt.title("Top Inventors")
plt.xlabel("Inventor")
plt.ylabel("Patent Count")

plt.tight_layout()

plt.savefig(VIS_DIR / "top_inventors.png")

print("✓ top_inventors.png saved")


# ─────────────────────────────────────────────
# Q2 TOP COMPANIES
# ─────────────────────────────────────────────

query = """
SELECT
    c.name,
    COUNT(pr.patent_id) AS patent_count

FROM companies c

JOIN patent_relationships pr
    ON c.company_id = pr.company_id

GROUP BY c.name
ORDER BY patent_count DESC
LIMIT 10;
"""

df = pd.read_sql(query, engine)

plt.figure(figsize=(12, 6))

plt.bar(df["name"], df["patent_count"])

plt.xticks(rotation=45)

plt.title("Top Companies")
plt.xlabel("Company")
plt.ylabel("Patent Count")

plt.tight_layout()

plt.savefig(VIS_DIR / "top_companies.png")

print("✓ top_companies.png saved")


# ─────────────────────────────────────────────
# Q3 COUNTRIES
# ─────────────────────────────────────────────

query = """
SELECT
    country,
    COUNT(*) AS patent_count

FROM inventors

GROUP BY country
ORDER BY patent_count DESC
LIMIT 10;
"""

df = pd.read_sql(query, engine)

plt.figure(figsize=(10, 6))

plt.bar(df["country"], df["patent_count"])

plt.title("Top Patent-Producing Countries")
plt.xlabel("Country")
plt.ylabel("Patent Count")

plt.tight_layout()

plt.savefig(VIS_DIR / "countries.png")

print("✓ countries.png saved")


# ─────────────────────────────────────────────
# Q4 TRENDS OVER TIME
# ─────────────────────────────────────────────

query = """
SELECT
    year,
    COUNT(*) AS patents_per_year

FROM patents

GROUP BY year
ORDER BY year;
"""

df = pd.read_sql(query, engine)

plt.figure(figsize=(12, 6))

plt.plot(df["year"], df["patents_per_year"])

plt.title("Patent Trends Over Time")
plt.xlabel("Year")
plt.ylabel("Patents")

plt.tight_layout()

plt.savefig(VIS_DIR / "patents_per_year.png")

print("✓ patents_per_year.png saved")