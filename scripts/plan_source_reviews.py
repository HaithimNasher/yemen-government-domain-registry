#!/usr/bin/env python3
"""Create a deterministic source-review queue."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "reports/v017-source-gaps.json"
OUTPUT = ROOT / "reports/v017-source-review-queue.json"

PRIORITY = {
    "universities.json": 1,
    "government_bodies.json": 2,
    "banks_candidates.json": 3,
    "ministries.json": 4,
    "governorates.json": 5,
    "public_corporations.json": 6,
    "government_services.json": 7,
}

def main():
    report = json.loads(INPUT.read_text(encoding="utf-8"))

    records = report["missing_records"]
    queue = []

    for record in records:
        filename = record["source_file"]

        queue.append({
            "entity_id": record["entity_id"],
            "name": record["name"],
            "source_file": filename,
            "priority": PRIORITY.get(filename, 99),
            "review_status": "pending",
            "candidate_source_url": None,
            "review_notes": None,
        })

    queue.sort(
        key=lambda item: (
            item["priority"],
            str(item["entity_id"]),
        )
    )

    if len(queue) != report["missing_source_count"]:
        raise ValueError("Source gap count mismatch")

    ids = [item["entity_id"] for item in queue]

    if any(not isinstance(i, str) or not i for i in ids):
        raise ValueError("Missing entity_id in review queue")

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate entity IDs in review queue")

    result = {
        "version": "0.17.0",
        "total_pending": len(queue),
        "priority_counts": dict(
            sorted(Counter(
                str(item["priority"]) for item in queue
            ).items(), key=lambda x: int(x[0]))
        ),
        "records": queue,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("YNDR v0.17 SOURCE REVIEW QUEUE")
    print("Pending:", len(queue))

    for priority, count in result["priority_counts"].items():
        print(f"Priority {priority}: {count}")

    print("Report:", OUTPUT)


if __name__ == "__main__":
    main()
