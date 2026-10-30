import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from validate_evidence_reviews import validate

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_TRANSITIONS = {
    "needs_more_information": {
        "needs_more_information",
        "accepted_for_review",
        "rejected",
    },
    "accepted_for_review": {
        "accepted_for_review",
        "needs_more_information",
        "rejected",
    },
    "rejected": {
        "rejected",
    },
}


def validate_transitions(reviews, evidence_ids):
    errors = validate(reviews, evidence_ids)

    if not isinstance(reviews, list):
        return errors

    grouped = defaultdict(list)

    for index, record in enumerate(reviews):
        if not isinstance(record, dict):
            continue

        evidence_id = record.get("evidence_id")
        reviewed_at = record.get("reviewed_at")
        decision = record.get("decision")

        if not all(isinstance(v, str) for v in (
            evidence_id, reviewed_at, decision
        )):
            continue

        try:
            review_date = date.fromisoformat(reviewed_at)
        except ValueError:
            continue

        grouped[evidence_id].append(
            (review_date, index, decision)
        )

    for evidence_id, entries in grouped.items():
        entries.sort(key=lambda item: (item[0], item[1]))

        for previous, current in zip(entries, entries[1:]):
            if previous[0] == current[0] and previous[2] != current[2]:
                errors.append(
                    f"Evidence {evidence_id}: ambiguous same-day "
                    "review decisions"
                )
                continue

            old_decision = previous[2]
            new_decision = current[2]

            allowed = ALLOWED_TRANSITIONS.get(old_decision, set())

            if new_decision not in allowed:
                errors.append(
                    f"Evidence {evidence_id}: invalid transition "
                    f"{old_decision} -> {new_decision}"
                )

    return errors


def main():
    reviews = json.loads(
        (ROOT / "data/governance/evidence_reviews.json")
        .read_text(encoding="utf-8")
    )

    evidence = json.loads(
        (ROOT / "data/governance/evidence_registry.json")
        .read_text(encoding="utf-8")
    )

    evidence_ids = {
        item["evidence_id"]
        for item in evidence
        if isinstance(item, dict)
        and isinstance(item.get("evidence_id"), str)
    }

    errors = validate_transitions(reviews, evidence_ids)

    print("YNDR REVIEW TRANSITION VALIDATION")
    print(f"Reviews: {len(reviews)}")
    print(f"Errors: {len(errors)}")

    for error in errors:
        print("ERROR:", error)

    if errors:
        sys.exit(1)

    print("REVIEW TRANSITION VALIDATION: PASS")


if __name__ == "__main__":
    main()
