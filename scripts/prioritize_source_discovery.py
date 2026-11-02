#!/usr/bin/env python3
"""Read-only prioritized official-source discovery work queue."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from scripts.build_source_discovery_queue import (
    build_queue,
    load_records,
)
from scripts.enrich_source_discovery_queue import enrich_queue

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = ROOT / "data/governance"

FIELDS = [
    "priority",
    "priority_reason",
    "entity_id",
    "name_ar",
    "name_en",
    "source_file",
    "verification_status",
    "candidate_count",
    "evidence_count",
    "review_count",
    "discovery_status",
]

# Operational search priority, not a verification score.
PRIORITY_FILES = {
    "ministries.json": 1,
    "governorates.json": 2,
    "districts.json": 3,
    "universities.json": 4,
}


def priority_for(record):
    source_file = record["source_file"]
    return PRIORITY_FILES.get(source_file, 5)


def build_prioritized_queue(
    reviews,
    candidates,
    evidence,
    evidence_reviews,
    enrich=True,
):
    queue = build_queue(reviews, candidates)

    if enrich:
        queue = enrich_queue(queue)

    evidence_count = Counter()
    review_count = Counter()

    evidence_to_entity = {}

    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("Invalid evidence record")

        evidence_id = item.get("evidence_id")
        entity_id = item.get("entity_id")

        if not isinstance(evidence_id, str) or not evidence_id:
            raise ValueError("Invalid evidence_id")

        if not isinstance(entity_id, str) or not entity_id:
            raise ValueError("Invalid evidence entity_id")

        if evidence_id in evidence_to_entity:
            raise ValueError("Duplicate evidence_id")

        evidence_to_entity[evidence_id] = entity_id
        evidence_count[entity_id] += 1

    for item in evidence_reviews:
        if not isinstance(item, dict):
            raise ValueError("Invalid evidence review record")

        evidence_id = item.get("evidence_id")

        if evidence_id not in evidence_to_entity:
            raise ValueError(
                f"Unknown reviewed evidence: {evidence_id}"
            )

        entity_id = evidence_to_entity[evidence_id]
        review_count[entity_id] += 1

    result = []

    for item in queue:
        entity_id = item["entity_id"]
        priority = priority_for(item)

        if item["candidate_count"]:
            reason = "candidate_review_needed"
        elif evidence_count[entity_id]:
            reason = "evidence_review_needed"
        else:
            reason = "official_source_discovery_needed"

        result.append({
            **item,
            "priority": priority,
            "priority_reason": reason,
            "evidence_count": evidence_count[entity_id],
            "review_count": review_count[entity_id],
        })

    return sorted(
        result,
        key=lambda item: (
            item["candidate_count"] > 0,
            item["evidence_count"] > 0,
            item["priority"],
            item["entity_id"],
        ),
    )


def export_csv(records, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if args.limit < 0:
        parser.error("--limit must be non-negative")

    reviews = load_records(
        GOVERNANCE / "source_reviews.json"
    )
    candidates = load_records(
        GOVERNANCE / "source_candidates.json"
    )
    evidence = load_records(
        GOVERNANCE / "evidence_registry.json"
    )
    evidence_reviews = load_records(
        GOVERNANCE / "evidence_reviews.json"
    )

    queue = build_prioritized_queue(
        reviews,
        candidates,
        evidence,
        evidence_reviews,
    )

    print("YNDR v0.22 PRIORITIZED SOURCE DISCOVERY")
    print("Entities:", len(queue))
    print(
        "Without candidates:",
        sum(x["candidate_count"] == 0 for x in queue),
    )

    for item in queue[:args.limit]:
        print(
            item["priority"],
            item["entity_id"],
            item.get("name_ar") or item.get("name_en"),
            item["priority_reason"],
        )

    if args.output:
        export_csv(queue, args.output)
        print("CSV:", args.output)


if __name__ == "__main__":
    main()
