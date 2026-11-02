#!/usr/bin/env python3
"""Export source discovery work queue without changing registries."""

import argparse
import csv
import json
from pathlib import Path

from scripts.build_source_discovery_queue import (
    build_queue,
    load_records,
)
from scripts.enrich_source_discovery_queue import (
    enrich_queue,
)

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "entity_id",
    "name_ar",
    "name_en",
    "source_file",
    "verification_status",
    "candidate_count",
    "discovery_status",
]


def export_queue(output):
    reviews = load_records(
        ROOT / "data/governance/source_reviews.json"
    )
    candidates = load_records(
        ROOT / "data/governance/source_candidates.json"
    )

    queue = enrich_queue(
        build_queue(reviews, candidates)
    )

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(queue)

    return len(queue)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    count = export_queue(args.output)

    print("YNDR SOURCE DISCOVERY EXPORT")
    print("Entities:", count)
    print("Output:", args.output)


if __name__ == "__main__":
    main()
