import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

catalog_path = DATA / "governance/government_bodies_domain_catalog.json"
output_path = DATA / "government_bodies.json"
db_path = DATA / "registry.db"

catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

with sqlite3.connect(db_path) as conn:
    existing = conn.execute(
        "SELECT entity_id, name_ar, domain FROM entities"
    ).fetchall()

existing_ids = {r[0] for r in existing}
existing_names = {r[1].strip() for r in existing}
existing_domains = {r[2].lower() for r in existing if r[2]}

records = []
skipped = []
seen_ids = set()
seen_names = set()
seen_domains = set()

for item in catalog:
    entity_id = item["entity_id"]
    name_ar = item["name_ar"].strip()
    proposed_domain = item["proposed_domain"].lower().strip()

    if (
        entity_id in existing_ids
        or name_ar in existing_names
        or proposed_domain in existing_domains
        or entity_id in seen_ids
        or name_ar in seen_names
        or proposed_domain in seen_domains
    ):
        skipped.append({
            "entity_id": entity_id,
            "name_ar": name_ar,
            "proposed_domain": proposed_domain,
            "reason": "Existing or duplicate entity/domain"
        })
        continue

    records.append({
        "entity_id": entity_id,
        "name_ar": name_ar,
        "name_en": name_ar,
        "category": item["category"],
        "parent_entity_id": None,
        "domain": proposed_domain,
        "domain_status": "proposed",
        "ownership_verified": False,
        "source_url": None,
        "last_verified": None
    })

    seen_ids.add(entity_id)
    seen_names.add(name_ar)
    seen_domains.add(proposed_domain)

print("Catalog:", len(catalog))
print("New candidates:", len(records))
print("Skipped:", len(skipped))

for item in skipped:
    print("REVIEW:", item)

if skipped:
    print("Import halted: resolve duplicates before writing.")
    raise SystemExit(1)

output_path.write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("Created:", output_path)
