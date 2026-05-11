"""
05_generate_reports.py
~~~~~~~~~~~~~~~~~~~~~~
Generates dataset profiling reports in:

    ✓ Console
    ✓ CSV
    ✓ JSON

For every cleaned patent dataset.

Reports include:
    - Row counts
    - Column counts
    - Missing values
    - Duplicate rows
    - Unique values
    - Data types
    - Memory usage
    - Numeric statistics
    - Text statistics

Outputs:
    data/reports/
        ├── csv/
        ├── json/
        └── console/

Run:
    python scripts/05_generate_reports.py
"""

import json
import pandas as pd
from pathlib import Path


# CONFIG

BASE_DIR = Path(__file__).resolve().parent.parent

CLEAN_DIR = BASE_DIR / "data" / "cleaned"

REPORT_DIR = BASE_DIR / "data" / "reports"
CSV_REPORT_DIR = REPORT_DIR / "csv"
JSON_REPORT_DIR = REPORT_DIR / "json"
CONSOLE_REPORT_DIR = REPORT_DIR / "console"

CSV_REPORT_DIR.mkdir(parents=True, exist_ok=True)
JSON_REPORT_DIR.mkdir(parents=True, exist_ok=True)
CONSOLE_REPORT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "clean_patents.csv",
    "clean_applications.csv",
    "clean_abstracts.csv",
    "clean_inventors.csv",
    "clean_assignees.csv",
    "clean_locations.csv",
]


# -------------- ANALYZE DATASET ---------------

def analyze_dataset(file_path):

    print("\n" + "=" * 80)
    print(f" ANALYZING: {file_path.name}")
    print("=" * 80)

    df = pd.read_csv(file_path, low_memory=False)

    dataset_summary = {
        "dataset_name": file_path.name,
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2
        ),
        "columns_info": [],
        "numeric_statistics": {},
        "text_statistics": {},
    }

    # ------------ COLUMN INFO ------------

    for col in df.columns:

        missing = int(df[col].isna().sum())

        missing_pct = round(
            (missing / len(df)) * 100,
            2
        )

        unique_values = int(
            df[col].nunique(dropna=True)
        )

        column_info = {
            "column": col,
            "dtype": str(df[col].dtype),
            "missing_values": missing,
            "missing_percent": missing_pct,
            "unique_values": unique_values,
        }

        dataset_summary["columns_info"].append(column_info)

    # ------ NUMERIC STATISTICS -----------

    numeric_cols = df.select_dtypes(include=["number"]).columns

    for col in numeric_cols:

        stats = {
            "count": float(df[col].count()),
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
        }

        dataset_summary["numeric_statistics"][col] = stats


    # ------------ TEXT STATISTICS -------------

    text_cols = df.select_dtypes(include=["object"]).columns

    for col in text_cols:

        lengths = df[col].astype(str).str.len()

        stats = {
            "avg_length": round(float(lengths.mean()), 2),
            "min_length": int(lengths.min()),
            "max_length": int(lengths.max()),
        }

        dataset_summary["text_statistics"][col] = stats

    return df, dataset_summary


# ------------ SAVE CSV REPORT -------------

def save_csv_report(summary, dataset_name):

    column_df = pd.DataFrame(summary["columns_info"])

    output_path = (
        CSV_REPORT_DIR /
        f"{dataset_name}_columns_report.csv"
    )

    column_df.to_csv(output_path, index=False)

    print(f"✓ CSV report saved → {output_path.name}")


# --------- SAVE JSON REPORT -----------

def save_json_report(summary, dataset_name):

    output_path = (
        JSON_REPORT_DIR /
        f"{dataset_name}_summary.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print(f"✓ JSON report saved → {output_path.name}")


# -------- SAVE CONSOLE REPORT ----------

def save_console_report(df, summary, dataset_name):

    lines = []

    lines.append("=" * 80)
    lines.append(f"DATASET: {dataset_name}")
    lines.append("=" * 80)

    lines.append(f"\nRows: {summary['rows']:,}")
    lines.append(f"Columns: {summary['columns']:,}")
    lines.append(
        f"Duplicate Rows: {summary['duplicate_rows']:,}"
    )

    lines.append(
        f"Memory Usage: "
        f"{summary['memory_usage_mb']} MB"
    )

    # COLUMN INFO
    lines.append("\nCOLUMN INFORMATION")
    lines.append("-" * 80)

    for col in summary["columns_info"]:

        lines.append(
            f"\n{col['column']}"
            f"\n  Type: {col['dtype']}"
            f"\n  Missing: {col['missing_values']:,}"
            f"\n  Missing %: {col['missing_percent']}%"
            f"\n  Unique Values: {col['unique_values']:,}"
        )

    # NUMERIC STATS
    if summary["numeric_statistics"]:

        lines.append("\nNUMERIC STATISTICS")
        lines.append("-" * 80)

        for col, stats in summary["numeric_statistics"].items():

            lines.append(
                f"\n{col}"
                f"\n  Mean: {stats['mean']:.2f}"
                f"\n  Std: {stats['std']:.2f}"
                f"\n  Min: {stats['min']:.2f}"
                f"\n  Max: {stats['max']:.2f}"
            )

    # TEXT STATS
    if summary["text_statistics"]:

        lines.append("\nTEXT STATISTICS")
        lines.append("-" * 80)

        for col, stats in summary["text_statistics"].items():

            lines.append(
                f"\n{col}"
                f"\n  Avg Length: {stats['avg_length']}"
                f"\n  Min Length: {stats['min_length']}"
                f"\n  Max Length: {stats['max_length']}"
            )

    # SAMPLE ROWS
    lines.append("\nSAMPLE ROWS")
    lines.append("-" * 80)

    lines.append(df.head(5).to_string())

    report_text = "\n".join(lines)

    output_path = (
        CONSOLE_REPORT_DIR /
        f"{dataset_name}_console_report.txt"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"✓ Console report saved → {output_path.name}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():

    print("=" * 80)
    print(" PATENT DATASET REPORT GENERATOR")
    print("=" * 80)

    for file_name in FILES:

        file_path = CLEAN_DIR / file_name

        if not file_path.exists():

            print(f"\n⚠ Missing file: {file_name}")
            continue

        dataset_name = file_path.stem

        df, summary = analyze_dataset(file_path)

        # Save all report types
        save_csv_report(summary, dataset_name)
        save_json_report(summary, dataset_name)
        save_console_report(df, summary, dataset_name)

    print("\n" + "=" * 80)
    print(" ALL REPORTS GENERATED")
    print(f" Reports saved to: {REPORT_DIR.resolve()}")
    print("=" * 80)


if __name__ == "__main__":
    main()