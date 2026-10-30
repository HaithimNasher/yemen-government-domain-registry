import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FILES = [
    "ministries.json",
    "universities.json",
    "companies.json",
    "organizations.json",
]

records = []

for filename in FILES:
    path = DATA / filename

    if not path.exists():
        raise SystemExit(f"Missing file: {filename}")

    items = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(items, list):
        raise SystemExit(f"{filename} must contain a list")

    for item in items:
        if not isinstance(item, dict):
            raise SystemExit(f"Invalid record in {filename}")

        for field in ("entity_id", "name_ar", "name_en", "category"):
            if not item.get(field):
                raise SystemExit(
                    f"Missing {field} in {filename}"
                )

        if item.get("ownership_verified") is True:
            raise SystemExit(
                f"Ownership requires separate verification: "
                f"{item['entity_id']}"
            )

        records.append(item)

ids = [r["entity_id"] for r in records]
domains = [
    r["domain"].lower()
    for r in records
    if r.get("domain")
]

duplicate_ids = [
    value for value, count in Counter(ids).items()
    if count > 1
]

duplicate_domains = [
    value for value, count in Counter(domains).items()
    if count > 1
]

if duplicate_ids or duplicate_domains:
    print("Duplicate IDs:", duplicate_ids)
    print("Duplicate domains:", duplicate_domains)
    raise SystemExit("Validation failed")

print("Institution records:", len(records))
print("Unique IDs:", len(ids))
print("Unique domains:", len(domains))
print("VALIDATION: PASS")
