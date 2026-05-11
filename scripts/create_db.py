from pathlib import Path
from sqlalchemy import text
from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent

SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = f.read()

with engine.connect() as conn:

    conn.execute(text(schema))
    conn.commit()

print("✓ PostgreSQL tables created successfully")