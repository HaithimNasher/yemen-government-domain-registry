#!/usr/bin/env python3
"""Enrich source discovery queue with existing entity names."""

import json
from pathlib import Path

from scripts.build_source_discovery_queue import (
    build_queue,
    load_records,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_entity_names(source_file):
    path = DATA / source_file

    if not path.is_file():
        raise ValueError(
            f"Missing entity data file: {source_file}"
        )

    records = load_records(path)
    names = {}

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid entity record")

        entity_id = record.get(
            "entity_id",
            record.get("id"),
        )

        if not isinstance(entity_id, str):
            continue

        if entity_id in names:
            raise ValueError(
                f"Duplicate entity: {entity_id}"
            )

        names[entity_id] = {
            "name_ar": record.get("name_ar"),
            "name_en": record.get("name_en"),
        }

    return names


def enrich_queue(queue):
    cache = {}
    result = []

    for item in queue:
        source_file = item["source_file"]

        if source_file not in cache:
            cache[source_file] = load_entity_names(
                source_file
            )

        entity_id = item["entity_id"]

        names = cache[source_file].get(entity_id)

        if names is None:
            raise ValueError(
                f"Entity not found: {entity_id}"
            )

        result.append({
            **item,
            **names,
        })

    return result


def main():
    reviews = load_records(
        DATA / "governance/source_reviews.json"
    )
    candidates = load_records(
        DATA / "governance/source_candidates.json"
    )

    queue = build_queue(reviews, candidates)
    enriched = enrich_queue(queue)

    print("YNDR v0.19 ENRICHED SOURCE DISCOVERY")
    print("Entities:", len(enriched))

    for item in enriched[:15]:
        print(
            item["entity_id"],
            "|",
            item["name_ar"],
            "|",
            item["name_en"],
        )


if __name__ == "__main__":
    main()
