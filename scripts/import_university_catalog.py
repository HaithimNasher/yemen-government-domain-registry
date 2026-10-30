import json
import re
from pathlib import Path

main_path = Path("data/universities.json")
catalog_path = Path("data/governance/university_domain_catalog.json")

existing = json.loads(main_path.read_text(encoding="utf-8"))
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

assert isinstance(existing, list)
assert isinstance(catalog, list)
assert len(catalog) == 81, "Unexpected catalog size"

by_name = {r["name_ar"]: r for r in existing}
assert len(by_name) == len(existing), "Duplicate existing names"

used_ids = {r["entity_id"] for r in existing}
used_domains = {r["domain"] for r in existing}

new_records = []
matched = 0

for item in catalog:
    name = item["name_ar"]
    domain = item["proposed_domain"]

    if name in by_name:
        old = by_name[name]
        assert old["entity_id"] == item["entity_id"]
        assert old["domain"] == item["existing_domain"]
        matched += 1
        continue

    assert domain not in used_domains, f"Domain collision: {domain}"

    # Deterministic ID based on the proposed domain.
    slug = domain.removesuffix(".edu.ye")
    slug = re.sub(r"[^A-Za-z0-9]+", "-", slug).strip("-").upper()
    entity_id = f"YE-UNI-{slug}"

    assert entity_id not in used_ids, f"ID collision: {entity_id}"

    record = {
        "entity_id": entity_id,
        "name_ar": name,
        "name_en": item.get("name_en"),
        "category": item.get("category", "university"),
        "parent_entity_id": None,
        "domain": domain,
        "domain_status": "proposed",
        "ownership_verified": False,
        "source_url": None,
        "last_verified": None,
    }

    new_records.append(record)
    by_name[name] = record
    used_ids.add(entity_id)
    used_domains.add(domain)

print("Existing records:", len(existing))
print("Matched existing:", matched)
print("New records:", len(new_records))
print("Final records:", len(existing) + len(new_records))

assert matched == 3
assert len(new_records) == 78

# Preview only. No writes to the original registry.
preview_path = Path("reports/university_import_preview.json")
preview_path.parent.mkdir(parents=True, exist_ok=True)
preview_path.write_text(
    json.dumps(existing + new_records, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("Preview:", preview_path)
print("Original registry unchanged")
print("PASS")
