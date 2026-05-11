"""
04_dataset_summary.py
~~~~~~~~~~~~~~~~~~~~~
Generates detailed descriptive summaries for cleaned patent datasets.

Outputs:
    - Columns
    - Data types
    - Missing values
    - Duplicate counts
    - Numeric statistics
    - Memory usage
    - Sample rows
    - Unique value counts

Saves:
    reports/

Run:
    python scripts/04_dataset_summary.py
"""

import pandas as pd
from pathlib import Path


# CONFIGURATION

BASE_DIR = Path(__file__).resolve().parent.parent

CLEAN_DIR = BASE_DIR / "data" / "cleaned"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "clean_patents.csv",
    "clean_applications.csv",
    "clean_abstracts.csv",
    "clean_inventors.csv",
    "clean_assignees.csv",
    "clean_locations.csv",
]


# SUMMARY GENERATOR

def generate_summary(file_path):

    print("\n" + "=" * 80)
    print(f" ANALYZING: {file_path.name}")
    print("=" * 80)

    # Load dataset
    df = pd.read_csv(file_path, low_memory=False)

    report_lines = []

    
    # BASIC INFO


    report_lines.append(f"DATASET: {file_path.name}")
    report_lines.append("=" * 80)

    report_lines.append(f"\nRows: {len(df):,}")
    report_lines.append(f"Columns: {df.shape[1]:,}")

    memory_mb = df.memory_usage(deep=True).sum() / 1024**2
    report_lines.append(f"Memory Usage: {memory_mb:.2f} MB")

    
    # COLUMNS + DTYPES
    

    report_lines.append("\nCOLUMN INFORMATION")
    report_lines.append("-" * 80)

    for col in df.columns:

        dtype = df[col].dtype
        missing = df[col].isna().sum()
        missing_pct = (missing / len(df)) * 100

        unique = df[col].nunique(dropna=True)

        report_lines.append(
            f"{col}"
            f"\n   Type: {dtype}"
            f"\n   Missing: {missing:,} ({missing_pct:.2f}%)"
            f"\n   Unique Values: {unique:,}\n"
        )


    # DUPLICATES

    duplicates = df.duplicated().sum()

    report_lines.append("\nDUPLICATES")
    report_lines.append("-" * 80)
    report_lines.append(f"Duplicate Rows: {duplicates:,}")

    
    # NUMERIC STATISTICS

    numeric_cols = df.select_dtypes(include=["number"]).columns

    if len(numeric_cols) > 0:

        report_lines.append("\nNUMERIC STATISTICS")
        report_lines.append("-" * 80)

        stats = df[numeric_cols].describe().transpose()

        report_lines.append(stats.to_string())


    # TEXT COLUMN ANALYSIS

    text_cols = df.select_dtypes(include=["object"]).columns

    if len(text_cols) > 0:

        report_lines.append("\nTEXT COLUMN ANALYSIS")
        report_lines.append("-" * 80)

        for col in text_cols:

            lengths = df[col].astype(str).str.len()

            report_lines.append(
                f"\n{col}"
                f"\n   Avg Length: {lengths.mean():.2f}"
                f"\n   Max Length: {lengths.max():.2f}"
                f"\n   Min Length: {lengths.min():.2f}"
            )

    # SAMPLE ROWS

    report_lines.append("\nSAMPLE ROWS")
    report_lines.append("-" * 80)

    report_lines.append(df.head(5).to_string())

    
    # SAVE REPORT
    

    report_text = "\n".join(report_lines)

    report_file = REPORT_DIR / f"{file_path.stem}_summary.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"✓ Report saved → {report_file.name}")

    # Console preview
    print(f"\nRows: {len(df):,}")
    print(f"Columns: {df.shape[1]}")
    print(f"Memory Usage: {memory_mb:.2f} MB")
    print(f"Duplicate Rows: {duplicates:,}")


# MAIN

def main():

    print("=" * 80)
    print(" PATENT DATASET DESCRIPTIVE ANALYSIS")
    print("=" * 80)

    for file_name in FILES:

        file_path = CLEAN_DIR / file_name

        if file_path.exists():
            generate_summary(file_path)
        else:
            print(f"\n⚠ Missing file: {file_name}")

    print("\n" + "=" * 80)
    print(" ANALYSIS COMPLETE")
    print(f" Reports saved to: {REPORT_DIR.resolve()}")
    print("=" * 80)


if __name__ == "__main__":
    main()