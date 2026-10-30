import json
from collections import Counter
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

records = []
issues = []

for filename in FILES:
    path = DATA / filename

    if not path.exists():
        issues.append({
            "severity": "error",
            "file": filename,
            "message": "Missing source file"
        })
        continue

    items = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(items, list):
        issues.append({
            "severity": "error",
            "file": filename,
            "message": "Expected JSON array"
        })
        continue

    for item in items:
        records.append((filename, item))

ids = [
    item.get("entity_id")
    for _, item in records
    if item.get("entity_id")
]

domains = [
    str(item["domain"]).lower().rstrip(".")
    for _, item in records
    if item.get("domain")
]

duplicate_ids = {
    value for value, count in Counter(ids).items()
    if count > 1
}

duplicate_domains = {
    value for value, count in Counter(domains).items()
    if count > 1
}

for filename, item in records:
    entity_id = item.get("entity_id")

    if not entity_id:
        issues.append({
            "severity": "error",
            "file": filename,
            "message": "Missing entity_id"
        })

    if entity_id in duplicate_ids:
        issues.append({
            "severity": "error",
            "entity_id": entity_id,
            "message": "Duplicate entity ID"
        })

    domain = item.get("domain")

    if domain and str(domain).lower().rstrip(".") in duplicate_domains:
        issues.append({
            "severity": "error",
            "entity_id": entity_id,
            "message": "Duplicate domain"
        })

    if item.get("ownership_verified") is True:
        issues.append({
            "severity": "warning",
            "entity_id": entity_id,
            "message": "Ownership claim requires evidence"
        })

    if item.get("category") in {
        "ministry", "university", "company", "organization"
    }:
        if not item.get("source_url"):
            issues.append({
                "severity": "warning",
                "entity_id": entity_id,
                "message": "Missing source URL"
            })

    name = str(item.get("name_en") or "").lower()

    if "example" in name or "test university" in name:
        issues.append({
            "severity": "error",
            "entity_id": entity_id,
            "message": "Possible placeholder entity"
        })

report = {
    "project": "YNDR",
    "audit_version": "0.5.0",
    "total_records": len(records),
    "errors": sum(
        i["severity"] == "error" for i in issues
    ),
    "warnings": sum(
        i["severity"] == "warning" for i in issues
    ),
    "issues": issues
}

output = ROOT / "data-quality-report.json"

output.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("YNDR DATA QUALITY AUDIT")
print("Records:", report["total_records"])
print("Errors:", report["errors"])
print("Warnings:", report["warnings"])
print("Report:", output)

if report["errors"]:
    raise SystemExit(1)

print("AUDIT: PASS (no structural errors)")
