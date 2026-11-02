#!/usr/bin/env python3
"""Validate human source-review decisions without approving sources."""

import json
from datetime import date
from pathlib import Path

from scripts.add_source_candidate import validate_url

ROOT = Path(__file__).resolve().parents[1]

DECISIONS = ROOT / "data/governance/source_review_decisions.json"
CANDIDATES = ROOT / "data/governance/source_candidates.json"
REVIEWS = ROOT / "data/governance/source_reviews.json"

ALLOWED_DECISIONS = {
    "accepted",
    "rejected",
    "needs_more_evidence",
}


def validate(records, candidates, reviews):
    errors = []

    if not isinstance(records, list):
        return ["Decision records must be a list"]

    if not isinstance(candidates, list):
        return ["Candidate records must be a list"]

    if not isinstance(reviews, list):
        return ["Source reviews must be a list"]

    review_ids = {
        r["entity_id"]
        for r in reviews
        if isinstance(r, dict)
        and isinstance(r.get("entity_id"), str)
    }

    candidate_pairs = {
        (r.get("entity_id"), r.get("candidate_source_url"))
        for r in candidates
        if isinstance(r, dict)
    }

    seen = set()
    candidate_decisions = {}

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"Record {index}: invalid object")
            continue

        decision_id = record.get("decision_id")

        if not isinstance(decision_id, str) or not decision_id.strip():
            errors.append(f"Record {index}: missing decision_id")
        elif decision_id in seen:
            errors.append(f"Record {index}: duplicate decision_id")
        else:
            seen.add(decision_id)

        entity_id = record.get("entity_id")
        url = record.get("candidate_source_url")

        if entity_id not in review_ids:
            errors.append(f"Record {index}: unknown entity")

        try:
            validate_url(url)
        except (ValueError, TypeError):
            errors.append(f"Record {index}: invalid URL")

        if (entity_id, url) not in candidate_pairs:
            errors.append(f"Record {index}: candidate not registered")

        pair = (entity_id, url)
        if pair in candidate_decisions:
            errors.append(
                f"Record {index}: multiple decisions for same candidate"
            )
        else:
            candidate_decisions[pair] = index

        if record.get("decision") not in ALLOWED_DECISIONS:
            errors.append(f"Record {index}: invalid decision")

        reviewer = record.get("reviewed_by")
        if not isinstance(reviewer, str) or not reviewer.strip():
            errors.append(f"Record {index}: missing reviewer")

        notes = record.get("review_notes")
        if not isinstance(notes, str) or not notes.strip():
            errors.append(f"Record {index}: missing review notes")

        reviewed_at = record.get("reviewed_at")
        if not isinstance(reviewed_at, str):
            errors.append(f"Record {index}: invalid review date")
        else:
            try:
                parsed = date.fromisoformat(reviewed_at)
                if parsed.isoformat() != reviewed_at:
                    raise ValueError("Noncanonical date")
                if parsed > date.today():
                    errors.append(f"Record {index}: future review date")
            except ValueError:
                errors.append(f"Record {index}: invalid review date")

        if record.get("ownership_verified") is not False:
            errors.append(
                f"Record {index}: ownership must remain unverified"
            )

    return errors


def main():
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    reviews = json.loads(REVIEWS.read_text(encoding="utf-8"))

    if not isinstance(decisions, dict) or not isinstance(candidates, dict):
        raise ValueError("Invalid registry structure")

    errors = validate(
        decisions.get("records"),
        candidates.get("records"),
        reviews,
    )

    print("YNDR v0.18 SOURCE DECISION VALIDATION")
    print("Decisions:", len(decisions.get("records", [])))
    print("Errors:", len(errors))

    for error in errors:
        print("ERROR:", error)

    if errors:
        raise SystemExit(1)

    print("SOURCE DECISION VALIDATION: PASS")


if __name__ == "__main__":
    main()
