#!/usr/bin/env python3
"""Report missing source URLs without modifying registry data."""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.audit_sources import FILES
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from audit_sources import FILES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "reports" / "v017-source-gaps.json"


def build_report():
    missing = []
    counts = Counter()
    total = 0

    for filename in FILES:
        path = DATA / filename
        records = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(records, list):
            raise ValueError(f"{filename} must contain a list")

        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"Invalid record in {filename}")

            total += 1

            if not record.get("source_url"):
                counts[filename] += 1

                missing.append({
                    "entity_id": record.get("entity_id"),
                    "name": (
                        record.get("name_ar")
                        or record.get("name_en")
                        or record.get("name")
                    ),
                    "source_file": filename,
                    "reason": "missing_source_url",
                })

    return {
        "report_version": "0.17.0",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_entities": total,
        "missing_source_count": len(missing),
        "missing_by_file": dict(sorted(counts.items())),
        "missing_records": missing,
    }


def main():
    report = build_report()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("YNDR v0.17 SOURCE GAP REPORT")
    print("Total entities:", report["total_entities"])
    print("Missing sources:", report["missing_source_count"])

    for filename, count in report["missing_by_file"].items():
        print(f"  {filename}: {count}")

    print("Report:", OUTPUT)


if __name__ == "__main__":
    main()
