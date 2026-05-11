import pandas as pd
from pathlib import Path
from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent

CLEAN_DIR = BASE_DIR / "data" / "cleaned"

# ─────────────────────────────────────────────
# LOAD PATENTS
# ─────────────────────────────────────────────

print("\nLoading patents...")

patents = pd.read_csv(
    CLEAN_DIR / "clean_patents.csv",
    low_memory=False
)

abstracts = pd.read_csv(
    CLEAN_DIR / "clean_abstracts.csv",
    low_memory=False
)

applications = pd.read_csv(
    CLEAN_DIR / "clean_applications.csv",
    low_memory=False
)

patents = patents.merge(
    abstracts,
    on="patent_id",
    how="left"
)

patents = patents.merge(
    applications,
    on="patent_id",
    how="left"
)

patents = patents[
    [
        "patent_id",
        "title",
        "abstract",
        "filing_date",
        "year"
    ]
]

patents.to_sql(
    "patents",
    engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("✓ patents loaded")


# ─────────────────────────────────────────────
# LOAD INVENTORS
# ─────────────────────────────────────────────

print("\nLoading inventors...")

inventors = pd.read_csv(
    CLEAN_DIR / "clean_inventors.csv",
    low_memory=False
)

locations = pd.read_csv(
    CLEAN_DIR / "clean_locations.csv",
    low_memory=False
)

inventors = inventors.merge(
    locations,
    left_on="inventor_location_id",
    right_on="location_id",
    how="left"
)

inventors_table = inventors[
    [
        "inventor_id",
        "name",
        "country"
    ]
].copy()

# Remove rows missing inventor_id
inventors_table = inventors_table.dropna(
    subset=["inventor_id"]
)

# Keep first occurrence of each inventor_id
inventors_table = inventors_table.drop_duplicates(
    subset="inventor_id",
    keep="first"
)

inventors_table.to_sql(
    "inventors",
    engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("✓ inventors loaded")


# ─────────────────────────────────────────────
# LOAD COMPANIES
# ─────────────────────────────────────────────

print("\nLoading companies...")

companies = pd.read_csv(
    CLEAN_DIR / "clean_assignees.csv",
    low_memory=False
)

companies_table = companies[
    [
        "company_id",
        "name"
    ]
].copy()

companies_table = companies_table.dropna(
    subset=["company_id"]
)

companies_table = companies_table.drop_duplicates(
    subset="company_id",
    keep="first"
)

companies_table.to_sql(
    "companies",
    engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("✓ companies loaded")


# ─────────────────────────────────────────────
# LOAD RELATIONSHIPS
# ─────────────────────────────────────────────

print("\nLoading relationships...")

relationships = inventors[
    [
        "patent_id",
        "inventor_id"
    ]
].copy()

relationships = relationships.merge(
    companies[
        [
            "patent_id",
            "company_id"
        ]
    ],
    on="patent_id",
    how="left"
)

relationships = relationships.drop_duplicates(
    subset=[
        "patent_id",
        "inventor_id",
        "company_id"
    ]
)

relationships.to_sql(
    "patent_relationships",
    engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("✓ relationships loaded")

print("\n✓ ALL DATA LOADED INTO POSTGRESQL")