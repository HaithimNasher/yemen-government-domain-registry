#!/usr/bin/env python3
"""Audit source metadata for YNDR entities."""

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "reports" / "source-audit.json"

FILES = [
    "governorates.json",
    "districts.json",
    "ministries.json",
    "universities.json",
    "government_services.json",
    "government_bodies.json",
    "public_corporations.json",
]

def audit():
    records = []
    missing = []
    invalid = []

    for filename in FILES:
        path = DATA / filename
        if not path.exists():
            print(f"WARNING: missing {filename}")
            continue

        content = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(content, list):
            raise ValueError(f"{filename} must contain a list")

        for item in content:
            if not isinstance(item, dict):
                raise ValueError(f"Invalid record in {filename}")

            entity_id = item.get("entity_id")
            source = item.get("source_url")
            records.append(item)

            if not source:
                missing.append({
                    "entity_id": entity_id,
                    "file": filename,
                    "reason": "missing_source_url"
                })
            elif not isinstance(source, str) or (
                urlparse(source).scheme not in ("http", "https")
                or not urlparse(source).netloc
            ):
                invalid.append({
                    "entity_id": entity_id,
                    "file": filename,
                    "source_url": source
                })

    report = {
        "version": "0.7.0",
        "total_records": len(records),
        "missing_sources": len(missing),
        "invalid_sources": len(invalid),
        "missing": missing,
        "invalid": invalid
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("YNDR SOURCE AUDIT")
    print("Records:", len(records))
    print("Missing sources:", len(missing))
    print("Invalid sources:", len(invalid))
    print("Report:", OUTPUT)

    return 1 if invalid else 0

if __name__ == "__main__":
    raise SystemExit(audit())
