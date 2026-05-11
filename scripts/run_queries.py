import json
import pandas as pd
from pathlib import Path
from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "outputs" / "query_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

queries = {

    "Q1_top_inventors": """
        SELECT
            i.name,
            COUNT(pr.patent_id) AS patent_count
        FROM inventors i
        JOIN patent_relationships pr
            ON i.inventor_id = pr.inventor_id
        GROUP BY i.name
        ORDER BY patent_count DESC
        LIMIT 10;
    """,

    "Q2_top_companies": """
        SELECT
            c.name,
            COUNT(pr.patent_id) AS patent_count
        FROM companies c
        JOIN patent_relationships pr
            ON c.company_id = pr.company_id
        GROUP BY c.name
        ORDER BY patent_count DESC
        LIMIT 10;
    """,

    "Q3_countries": """
        SELECT
            country,
            COUNT(*) AS patent_count
        FROM inventors
        GROUP BY country
        ORDER BY patent_count DESC;
    """,

    "Q4_trends_over_time": """
        SELECT
            year,
            COUNT(*) AS patents_per_year
        FROM patents
        GROUP BY year
        ORDER BY year;
    """,

    "Q5_join_query": """
        SELECT
            p.patent_id,
            p.title,
            i.name AS inventor,
            c.name AS company

        FROM patents p

        JOIN patent_relationships pr
            ON p.patent_id = pr.patent_id

        JOIN inventors i
            ON pr.inventor_id = i.inventor_id

        LEFT JOIN companies c
            ON pr.company_id = c.company_id

        LIMIT 20;
    """,

    "Q6_cte_query": """
        WITH inventor_patents AS (

            SELECT
                inventor_id,
                COUNT(*) AS patent_count

            FROM patent_relationships

            GROUP BY inventor_id
        )

        SELECT
            i.name,
            ip.patent_count

        FROM inventor_patents ip

        JOIN inventors i
            ON ip.inventor_id = i.inventor_id

        ORDER BY ip.patent_count DESC
        LIMIT 10;
    """,

    "Q7_ranking_query": """
        SELECT
            i.name,

            COUNT(pr.patent_id) AS patent_count,

            RANK() OVER (
                ORDER BY COUNT(pr.patent_id) DESC
            ) AS inventor_rank

        FROM inventors i

        JOIN patent_relationships pr
            ON i.inventor_id = pr.inventor_id

        GROUP BY i.name

        ORDER BY inventor_rank;
    """
}

for query_name, query in queries.items():

    print("\n" + "=" * 70)
    print(query_name)
    print("=" * 70)

    df = pd.read_sql(query, engine)

    print(df.head())

    # CSV
    csv_path = OUTPUT_DIR / f"{query_name}.csv"
    df.to_csv(csv_path, index=False)

    # JSON
    json_path = OUTPUT_DIR / f"{query_name}.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            df.to_dict(orient="records"),
            f,
            indent=4
        )

    # TXT
    txt_path = OUTPUT_DIR / f"{query_name}.txt"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(df.to_string())

    print(f"✓ Exported reports for {query_name}")

print("\n✓ ALL QUERIES EXECUTED SUCCESSFULLY")