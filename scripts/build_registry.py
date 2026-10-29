import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DB = DATA / "registry.db"

def build():
    with sqlite3.connect(DB) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id TEXT PRIMARY KEY,
            name_ar TEXT NOT NULL,
            name_en TEXT NOT NULL,
            category TEXT NOT NULL,
            parent_entity_id TEXT,
            domain TEXT UNIQUE,
            domain_status TEXT NOT NULL,
            ownership_verified INTEGER NOT NULL DEFAULT 0,
            source_url TEXT,
            last_verified TEXT,
            FOREIGN KEY(parent_entity_id)
                REFERENCES entities(entity_id)
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS national_domains (
            suffix TEXT PRIMARY KEY,
            category TEXT NOT NULL
        )
        """)

        suffixes = json.loads(
            (DATA / "national_domains.json").read_text(
                encoding="utf-8"
            )
        )
        for item in suffixes:
            conn.execute("""
            INSERT INTO national_domains(suffix, category)
            VALUES (?, ?)
            ON CONFLICT(suffix) DO UPDATE SET
            category=excluded.category
            """, (item["suffix"], item["category"]))

        for category in [
            "ministries", "governorates", "districts",
            "universities", "companies", "organizations"
        ]:
            path = DATA / f"{category}.json"
            if not path.exists():
                continue

            records = json.loads(path.read_text(encoding="utf-8"))
            for r in records:
                conn.execute("""
                INSERT INTO entities (
                    entity_id, name_ar, name_en, category,
                    parent_entity_id, domain, domain_status,
                    ownership_verified, source_url, last_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(entity_id) DO UPDATE SET
                    name_ar=excluded.name_ar,
                    name_en=excluded.name_en,
                    category=excluded.category,
                    parent_entity_id=excluded.parent_entity_id,
                    domain=excluded.domain,
                    domain_status=excluded.domain_status,
                    ownership_verified=excluded.ownership_verified,
                    source_url=excluded.source_url,
                    last_verified=excluded.last_verified
                """, (
                    r["entity_id"], r["name_ar"], r["name_en"],
                    r["category"], r.get("parent_entity_id"),
                    r.get("domain"), r["domain_status"],
                    int(r.get("ownership_verified", False)),
                    r.get("source_url"), r.get("last_verified")
                ))

        total = conn.execute(
            "SELECT COUNT(*) FROM entities"
        ).fetchone()[0]
        print(f"Database ready: {total} entities")

if __name__ == "__main__":
    build()
