import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FILES = [
    "governorates.json",
    "districts.json",
    "ministries.json",
    "universities.json",
    "companies.json",
    "organizations.json",
]

valid_ids = set()

for filename in FILES:
    path = DATA / filename

    if not path.exists():
        raise SystemExit(f"Missing source file: {path}")

    records = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(records, list):
        raise SystemExit(f"Expected JSON array: {filename}")

    for record in records:
        entity_id = record.get("entity_id")

        if not entity_id:
            raise SystemExit(f"Missing entity_id in {filename}")

        if entity_id in valid_ids:
            raise SystemExit(f"Duplicate entity_id: {entity_id}")

        valid_ids.add(entity_id)

db_path = DATA / "registry.db"

with sqlite3.connect(db_path) as db:
    db.execute("BEGIN")

    db.execute("""
        CREATE TEMP TABLE valid_entity_ids (
            entity_id TEXT PRIMARY KEY
        )
    """)

    db.executemany(
        "INSERT INTO valid_entity_ids VALUES (?)",
        [(entity_id,) for entity_id in sorted(valid_ids)]
    )

    stale = db.execute("""
        SELECT entity_id
        FROM entities
        WHERE entity_id NOT IN (
            SELECT entity_id FROM valid_entity_ids
        )
    """).fetchall()

    print("Source records:", len(valid_ids))
    print("Stale database records:", len(stale))

    for row in stale:
        print("STALE:", row[0])

    if stale:
        raise SystemExit(
            "Stale records found. Review them before deletion."
        )

    total = db.execute(
        "SELECT COUNT(*) FROM entities"
    ).fetchone()[0]

    if total != len(valid_ids):
        raise SystemExit(
            f"Count mismatch: database={total}, "
            f"sources={len(valid_ids)}"
        )

print("REGISTRY SYNC CHECK: PASS")
