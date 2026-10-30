import json
import sys
from collections import defaultdict
from pathlib import Path

from validate_evidence_reviews import validate

ROOT = Path(__file__).resolve().parents[1]


def audit(reviews, evidence_ids):
    errors = validate(reviews, evidence_ids)

    if not isinstance(reviews, list):
        return errors

    by_evidence = defaultdict(list)

    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            continue

        evidence_id = review.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            continue

        by_evidence[evidence_id].append((index, review))

    for evidence_id, entries in by_evidence.items():
        decisions = {
            record.get("decision")
            for _, record in entries
            if isinstance(record.get("decision"), str)
        }

        if (
            "accepted_for_review" in decisions
            and "rejected" in decisions
        ):
            errors.append(
                f"Evidence {evidence_id}: conflicting review decisions"
            )

    return errors


def main():
    reviews_path = ROOT / "data/governance/evidence_reviews.json"
    evidence_path = ROOT / "data/governance/evidence_registry.json"

    reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    evidence_ids = {
        record["evidence_id"]
        for record in evidence
        if isinstance(record, dict)
        and isinstance(record.get("evidence_id"), str)
    }

    errors = audit(reviews, evidence_ids)

    print("YNDR REVIEW INTEGRITY AUDIT")
    print(f"Reviews: {len(reviews)}")
    print(f"Errors: {len(errors)}")

    for error in errors:
        print("ERROR:", error)

    if errors:
        sys.exit(1)

    print("REVIEW INTEGRITY AUDIT: PASS")


if __name__ == "__main__":
    main()
