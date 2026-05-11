"""
02_clean_data.py
~~~~~~~~~~~~~~~~
Reads large raw TSV files from data/raw/, cleans them in CHUNKS with pandas,
and writes cleaned CSVs to data/cleaned/.

Optimized for:
    - Unzipped .tsv files
    - Large datasets (millions of rows)
    - Low memory usage

Key Improvements:
    ✓ Chunked processing
    ✓ Memory-efficient filtering
    ✓ Incremental CSV writing
    ✓ Handles huge TSV files safely
    ✓ No ZIP extraction required

Run:
    python scripts/02_clean_data.py
"""

import pandas as pd
from pathlib import Path

# CONFIGURATION

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "cleaned"

CLEAN_DIR.mkdir(parents=True, exist_ok=True)
CHUNK_SIZE = 100_000


# GENERIC PIPELINE

def chunk_reader(path, usecols=None):
    """
    Reads large TSV files in chunks.
    """
    return pd.read_csv(
        path,
        sep="\t",
        chunksize=CHUNK_SIZE,
        usecols=usecols,
        low_memory=False,
        on_bad_lines="skip",
        encoding="utf-8",
    )


def append_csv(df, output_path, first_chunk):
    """
    Append chunk to CSV incrementally.
    """
    df.to_csv(
        output_path,
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False,
    )


# CLEAN PATENTS

def clean_patents():
    print("\n[1/6] Cleaning patents...")

    input_path = RAW_DIR / "g_patent.tsv"
    output_path = CLEAN_DIR / "clean_patents.csv"

    patent_ids = set()

    first_chunk = True
    total_rows = 0

    for i, chunk in enumerate(chunk_reader(input_path), start=1):

        print(f"  Processing chunk {i:,}...")

        chunk = chunk.rename(columns={
            "patent_title": "title",
            "patent_date": "grant_date",
        })

        cols = ["patent_id", "title", "grant_date", "patent_type"]
        chunk = chunk[cols].copy()

        # Parse dates
        chunk["grant_date"] = pd.to_datetime(
            chunk["grant_date"],
            errors="coerce"
        )

        chunk["year"] = chunk["grant_date"].dt.year

        # Drop invalid rows
        chunk = chunk.dropna(
            subset=["patent_id", "title", "grant_date"]
        )

        chunk["title"] = chunk["title"].str.strip()

        # Deduplicate inside chunk
        chunk = chunk.drop_duplicates(subset="patent_id")

        # Format dates
        chunk["grant_date"] = chunk["grant_date"].dt.strftime("%Y-%m-%d")

        # Track patent IDs
        patent_ids.update(chunk["patent_id"].astype(str))

        append_csv(chunk, output_path, first_chunk)
        first_chunk = False

        total_rows += len(chunk)

        print(f"    Cleaned: {len(chunk):,} rows")

    print(f"  ✓ Saved {total_rows:,} cleaned patents")

    return patent_ids


# CLEAN APPLICATIONS

def clean_applications(patent_ids):
    print("\n[2/6] Cleaning applications...")

    input_path = RAW_DIR / "g_application.tsv"
    output_path = CLEAN_DIR / "clean_applications.csv"

    if not input_path.exists():
        print("  ⚠ g_application.tsv not found")
        return

    first_chunk = True
    total_rows = 0

    usecols = ["patent_id", "filing_date"]

    for i, chunk in enumerate(
        chunk_reader(input_path, usecols=usecols),
        start=1
    ):

        print(f"  Processing chunk {i:,}...")

        chunk["patent_id"] = chunk["patent_id"].astype(str)

        chunk = chunk[
            chunk["patent_id"].isin(patent_ids)
        ].copy()

        chunk["filing_date"] = pd.to_datetime(
            chunk["filing_date"],
            errors="coerce"
        )

        chunk = chunk.dropna(
            subset=["patent_id", "filing_date"]
        )

        chunk["filing_date"] = (
            chunk["filing_date"]
            .dt.strftime("%Y-%m-%d")
        )

        chunk = chunk.drop_duplicates(subset="patent_id")

        append_csv(chunk, output_path, first_chunk)
        first_chunk = False

        total_rows += len(chunk)

    print(f"  ✓ Saved {total_rows:,} cleaned applications")


# CLEAN ABSTRACTS

def clean_abstracts(patent_ids):
    print("\n[3/6] Cleaning abstracts...")

    input_path = RAW_DIR / "g_patent_abstract.tsv"
    output_path = CLEAN_DIR / "clean_abstracts.csv"

    if not input_path.exists():
        print("  ⚠ g_patent_abstract.tsv not found")
        return

    first_chunk = True
    total_rows = 0

    usecols = ["patent_id", "patent_abstract"]

    for i, chunk in enumerate(
        chunk_reader(input_path, usecols=usecols),
        start=1
    ):

        print(f"  Processing chunk {i:,}...")

        chunk = chunk.rename(columns={
            "patent_abstract": "abstract"
        })

        chunk["patent_id"] = chunk["patent_id"].astype(str)

        chunk = chunk[
            chunk["patent_id"].isin(patent_ids)
        ].copy()

        chunk = chunk.dropna(
            subset=["patent_id", "abstract"]
        )

        chunk["abstract"] = (
            chunk["abstract"]
            .astype(str)
            .str.strip()
        )

        chunk = chunk.drop_duplicates(subset="patent_id")

        append_csv(chunk, output_path, first_chunk)
        first_chunk = False

        total_rows += len(chunk)

    print(f"  ✓ Saved {total_rows:,} cleaned abstracts")


# CLEAN INVENTORS

def clean_inventors(patent_ids):
    print("\n[4/6] Cleaning inventors...")

    input_path = RAW_DIR / "g_inventor_disambiguated.tsv"
    output_path = CLEAN_DIR / "clean_inventors.csv"

    cols = [
        "patent_id",
        "inventor_id",
        "disambig_inventor_name_first",
        "disambig_inventor_name_last",
        "location_id",
    ]

    first_chunk = True
    total_rows = 0

    for i, chunk in enumerate(
        chunk_reader(input_path, usecols=cols),
        start=1
    ):

        print(f"  Processing chunk {i:,}...")

        chunk["patent_id"] = chunk["patent_id"].astype(str)

        chunk = chunk[
            chunk["patent_id"].isin(patent_ids)
        ].copy()

        chunk = chunk.dropna(
            subset=["patent_id", "inventor_id"]
        )

        chunk["name"] = (
            chunk["disambig_inventor_name_first"]
            .fillna("")
            .str.strip()
            + " "
            + chunk["disambig_inventor_name_last"]
            .fillna("")
            .str.strip()
        ).str.strip()

        chunk = chunk[
            chunk["name"].str.len() > 0
        ]

        chunk = chunk.rename(columns={
            "location_id": "inventor_location_id"
        })

        chunk = chunk[
            [
                "patent_id",
                "inventor_id",
                "name",
                "inventor_location_id",
            ]
        ]

        chunk = chunk.drop_duplicates()

        append_csv(chunk, output_path, first_chunk)
        first_chunk = False

        total_rows += len(chunk)

    print(f"  ✓ Saved {total_rows:,} cleaned inventors")


# CLEAN ASSIGNEES

def clean_assignees(patent_ids):
    print("\n[5/6] Cleaning assignees...")

    input_path = RAW_DIR / "g_assignee_disambiguated.tsv"
    output_path = CLEAN_DIR / "clean_assignees.csv"

    cols = [
        "patent_id",
        "assignee_id",
        "disambig_assignee_organization",
        "location_id",
    ]

    first_chunk = True
    total_rows = 0

    for i, chunk in enumerate(
        chunk_reader(input_path, usecols=cols),
        start=1
    ):

        print(f"  Processing chunk {i:,}...")

        chunk["patent_id"] = chunk["patent_id"].astype(str)

        chunk = chunk[
            chunk["patent_id"].isin(patent_ids)
        ].copy()

        chunk = chunk.dropna(
            subset=[
                "patent_id",
                "disambig_assignee_organization"
            ]
        )

        chunk["name"] = (
            chunk["disambig_assignee_organization"]
            .astype(str)
            .str.strip()
        )

        chunk = chunk.rename(columns={
            "assignee_id": "company_id",
            "location_id": "assignee_location_id",
        })

        chunk = chunk[
            [
                "patent_id",
                "company_id",
                "name",
                "assignee_location_id",
            ]
        ]

        chunk = chunk.drop_duplicates()

        append_csv(chunk, output_path, first_chunk)
        first_chunk = False

        total_rows += len(chunk)

    print(f"  ✓ Saved {total_rows:,} cleaned assignees")


# CLEAN LOCATIONS

def clean_locations():
    print("\n[6/6] Cleaning locations...")

    input_path = RAW_DIR / "g_location_disambiguated.tsv"
    output_path = CLEAN_DIR / "clean_locations.csv"

    cols = [
        "location_id",
        "disambig_city",
        "disambig_state",
        "disambig_country",
        "latitude",
        "longitude",
    ]

    first_chunk = True
    total_rows = 0

    for i, chunk in enumerate(
        chunk_reader(input_path, usecols=cols),
        start=1
    ):

        print(f"  Processing chunk {i:,}...")

        chunk = chunk.dropna(subset=["location_id"])

        chunk = chunk.rename(columns={
            "disambig_city": "city",
            "disambig_state": "state",
            "disambig_country": "country",
        })

        chunk["country"] = (
            chunk["country"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        chunk = chunk.drop_duplicates(subset="location_id")

        append_csv(chunk, output_path, first_chunk)
        first_chunk = False

        total_rows += len(chunk)

    print(f"  ✓ Saved {total_rows:,} cleaned locations")


# MAIN

def main():

    print("=" * 60)
    print(" PATENTSVIEW DATA CLEANER (CHUNKED VERSION)")
    print("=" * 60)

    patent_ids = clean_patents()

    print(f"\nTotal patent IDs loaded: {len(patent_ids):,}")

    clean_applications(patent_ids)
    clean_abstracts(patent_ids)
    clean_inventors(patent_ids)
    clean_assignees(patent_ids)
    clean_locations()

    print("\n" + "=" * 60)
    print(" CLEANING COMPLETE")
    print(f" Files saved to: {CLEAN_DIR.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()