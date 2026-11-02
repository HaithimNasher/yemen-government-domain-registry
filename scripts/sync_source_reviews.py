#!/usr/bin/env python3
"""Synchronize missing source reviews without verification claims."""

import argparse
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAPS = ROOT / "reports/v017-source-gaps.json"
REVIEWS = ROOT / "data/governance/source_reviews.json"


def build_updated_reviews(reviews, gaps):
    if not isinstance(reviews, list):
        raise ValueError("Source reviews must be a list")

    if not isinstance(gaps, list):
        raise ValueError("Source gaps must be a list")

    existing = set()

    for review in reviews:
        if not isinstance(review, dict):
            raise ValueError("Invalid review record")

        entity_id = review.get("entity_id")

        if not isinstance(entity_id, str) or not entity_id:
            raise ValueError("Invalid review entity_id")

        if entity_id in existing:
            raise ValueError(f"Duplicate review: {entity_id}")

        existing.add(entity_id)

    updated = list(reviews)
    added = []
    seen_gaps = set()

    for gap in gaps:
        if not isinstance(gap, dict):
            raise ValueError("Invalid source gap")

        entity_id = gap.get("entity_id")
        source_file = gap.get("source_file")

        if not isinstance(entity_id, str) or not entity_id:
            raise ValueError("Invalid gap entity_id")

        if not isinstance(source_file, str) or not source_file:
            raise ValueError("Invalid gap source_file")

        if entity_id in seen_gaps:
            raise ValueError(f"Duplicate source gap: {entity_id}")

        seen_gaps.add(entity_id)

        if entity_id in existing:
            continue

        review = {
            "entity_id": entity_id,
            "source_file": source_file,
            "verification_status": "unverified",
            "source_url": None,
            "source_type": None,
            "verified_at": None,
            "review_notes": "Source evidence required",
        }

        updated.append(review)
        added.append(entity_id)
        existing.add(entity_id)

    return updated, added


def atomic_write(path, records):
    fd, temp_name = tempfile.mkstemp(
        prefix=".source-reviews-",
        suffix=".tmp",
        dir=path.parent,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(
                records,
                handle,
                ensure_ascii=False,
                indent=2,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the updated source reviews",
    )
    args = parser.parse_args()

    current = json.loads(
        REVIEWS.read_text(encoding="utf-8")
    )

    report = json.loads(
        GAPS.read_text(encoding="utf-8")
    )

    updated, added = build_updated_reviews(
        current,
        report["missing_records"],
    )

    print("YNDR v0.17 SOURCE REVIEW SYNC")
    print("Existing reviews:", len(current))
    print("New reviews:", len(added))
    print("Total after sync:", len(updated))

    if not args.apply:
        print("MODE: DRY RUN")
        print("No files modified")
        return

    atomic_write(REVIEWS, updated)
    print("MODE: APPLY")
    print("Source reviews updated")


if __name__ == "__main__":
    main()
