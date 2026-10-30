#!/usr/bin/env python3
"""Audit proposed domains without claiming DNS ownership."""

import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "reports" / "domain-verification.json"

FILES = [
    "governorates.json",
    "districts.json",
    "ministries.json",
    "universities.json",
    "government_services.json",
]

def main():
    records = []

    for filename in FILES:
        path = DATA / filename
        items = json.loads(path.read_text(encoding="utf-8"))

        for item in items:
            domain = item.get("domain")

            if not domain:
                continue

            records.append({
                "entity_id": item["entity_id"],
                "domain": domain,
                "domain_status": item.get(
                    "domain_status", "unknown"
                ),
                "ownership_verified": item.get(
                    "ownership_verified", False
                ),
                "source_file": filename
            })

    counts = Counter(
        str(item["domain_status"])
        for item in records
    )

    verified = sum(
        item["ownership_verified"] is True
        for item in records
    )

    report = {
        "version": "0.7.0",
        "total_domains": len(records),
        "ownership_verified_count": verified,
        "status_counts": dict(counts),
        "records": records
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("YNDR DOMAIN VERIFICATION AUDIT")
    print("Domains:", len(records))
    print("Ownership verified flags:", verified)
    print("Statuses:", dict(counts))
    print("Report:", OUTPUT)


if __name__ == "__main__":
    main()
