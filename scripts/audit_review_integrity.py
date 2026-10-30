import json
import sys
from collections import defaultdict
from pathlib import Path

from validate_evidence_reviews import validate

ROOT = Path(__file__).resolve().parents[1]


def audit(reviews, evidence_ids):
    from validate_review_transitions import validate_transitions

    return validate_transitions(reviews, evidence_ids)


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
