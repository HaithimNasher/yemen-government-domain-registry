#!/usr/bin/env python3
"""Record a human review decision without verifying domain ownership."""

import argparse
import fcntl
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from uuid import uuid4

from scripts.validate_source_decisions import (
    CANDIDATES,
    DECISIONS,
    REVIEWS,
    validate,
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _record_decision_unlocked(
    entity_id,
    url,
    decision,
    reviewer,
    notes,
    decisions_path=DECISIONS,
    candidates_path=CANDIDATES,
    reviews_path=REVIEWS,
):
    if decision not in {
        "accepted", "rejected", "needs_more_evidence"
    }:
        raise ValueError("Invalid decision")

    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("Reviewer is required")

    if not isinstance(notes, str) or not notes.strip():
        raise ValueError("Review notes are required")

    registry = load_json(decisions_path)
    candidates_registry = load_json(candidates_path)
    reviews = load_json(reviews_path)

    if not isinstance(registry, dict):
        raise ValueError("Invalid decision registry")

    if not isinstance(candidates_registry, dict):
        raise ValueError("Invalid candidate registry")

    records = registry.get("records")
    candidates = candidates_registry.get("records")

    existing_errors = validate(records, candidates, reviews)
    if existing_errors:
        raise ValueError(
            "Existing registry invalid: "
            + "; ".join(existing_errors)
        )

    new_record = {
        "decision_id": "DEC-" + uuid4().hex,
        "entity_id": entity_id,
        "candidate_source_url": url,
        "decision": decision,
        "reviewed_by": reviewer.strip(),
        "reviewed_at": date.today().isoformat(),
        "review_notes": notes.strip(),
        "ownership_verified": False,
    }

    updated = records + [new_record]

    errors = validate(updated, candidates, reviews)
    if errors:
        raise ValueError("; ".join(errors))

    updated_registry = dict(registry)
    updated_registry["records"] = updated

    payload = (
        json.dumps(
            updated_registry,
            ensure_ascii=False,
            indent=2,
        ) + "\n"
    )

    # Atomic replacement on the same filesystem.
    fd, temporary = tempfile.mkstemp(
        prefix=".source-decisions-",
        suffix=".tmp",
        dir=str(decisions_path.parent),
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())

        os.replace(temporary, decisions_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

    return new_record



def locked_record_decision(**kwargs):
    """Serialize review writes across cooperating processes."""
    decisions_path = Path(
        kwargs.get("decisions_path", DECISIONS)
    )

    lock_path = decisions_path.with_name(
        decisions_path.name + ".lock"
    )

    with open(lock_path, "a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            return _record_decision_unlocked(**kwargs)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)



def record_decision(
    entity_id,
    url,
    decision,
    reviewer,
    notes,
    decisions_path=DECISIONS,
    candidates_path=CANDIDATES,
    reviews_path=REVIEWS,
):
    """Record a decision with exclusive file locking."""
    return locked_record_decision(
        entity_id=entity_id,
        url=url,
        decision=decision,
        reviewer=reviewer,
        notes=notes,
        decisions_path=decisions_path,
        candidates_path=candidates_path,
        reviews_path=reviews_path,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Record a human source review decision"
    )
    parser.add_argument("--entity-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument(
        "--decision",
        required=True,
        choices=[
            "accepted",
            "rejected",
            "needs_more_evidence",
        ],
    )
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--notes", required=True)

    args = parser.parse_args()

    record = locked_record_decision(
        entity_id=args.entity_id,
        url=args.url,
        decision=args.decision,
        reviewer=args.reviewer,
        notes=args.notes,
    )

    print("SOURCE REVIEW DECISION RECORDED")
    print("Decision ID:", record["decision_id"])
    print("Entity:", record["entity_id"])
    print("Decision:", record["decision"])
    print("Ownership verified: NO")


if __name__ == "__main__":
    main()
