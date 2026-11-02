#!/usr/bin/env python3
"""Build a read-only queue of entities requiring source discovery."""

import argparse
import json
from pathlib import Path

REVIEWS = Path("data/governance/source_reviews.json")
CANDIDATES = Path("data/governance/source_candidates.json")


def load_records(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    records = data.get("records", []) if isinstance(data, dict) else data

    if not isinstance(records, list):
        raise ValueError(f"Invalid records list: {path}")

    return records


def build_queue(reviews, candidates):
    candidate_counts = {}

    for candidate in candidates:
        entity_id = candidate.get("entity_id")
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise ValueError("Invalid candidate entity_id")

        candidate_counts[entity_id] = (
            candidate_counts.get(entity_id, 0) + 1
        )

    queue = []
    seen = set()

    for review in reviews:
        entity_id = review.get("entity_id")
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise ValueError("Invalid review entity_id")

        if entity_id in seen:
            raise ValueError(f"Duplicate review: {entity_id}")

        seen.add(entity_id)

        if review.get("verification_status") == "verified":
            continue

        count = candidate_counts.get(entity_id, 0)

        queue.append({
            "entity_id": entity_id,
            "source_file": review.get("source_file"),
            "verification_status": review.get(
                "verification_status"
            ),
            "candidate_count": count,
            "discovery_status": (
                "candidate_review_needed"
                if count else "source_discovery_needed"
            ),
        })

    return sorted(
        queue,
        key=lambda item: (
            item["candidate_count"] > 0,
            str(item["source_file"]),
            item["entity_id"],
        ),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reviews = load_records(REVIEWS)
    candidates = load_records(CANDIDATES)

    queue = build_queue(reviews, candidates)

    result = {
        "version": "0.19.0",
        "total": len(queue),
        "records": queue,
    }

    print("YNDR v0.19 SOURCE DISCOVERY QUEUE")
    print("Entities requiring review:", len(queue))
    print(
        "Without candidates:",
        sum(
            row["candidate_count"] == 0
            for row in queue
        ),
    )

    if args.output:
        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.output.write_text(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        print("Output:", args.output)


if __name__ == "__main__":
    main()
