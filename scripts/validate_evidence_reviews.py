import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REVIEWS_PATH = ROOT / "data/governance/evidence_reviews.json"
EVIDENCE_PATH = ROOT / "data/governance/evidence_registry.json"

ALLOWED_DECISIONS = {
    "accepted_for_review",
    "rejected",
    "needs_more_information",
}


def validate(reviews, evidence_ids):
    errors = []
    seen = set()

    if not isinstance(reviews, list):
        return ["Review registry must be a list"]

    for index, record in enumerate(reviews):
        if not isinstance(record, dict):
            errors.append(f"Record {index}: must be an object")
            continue

        for field in (
            "review_id",
            "evidence_id",
            "reviewer_id",
            "decision",
            "reviewed_at",
            "review_notes",
        ):
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"Record {index}: missing {field}")

        review_id = record.get("review_id")
        if isinstance(review_id, str) and review_id.strip():
            if review_id in seen:
                errors.append(f"Record {index}: duplicate review_id")
            seen.add(review_id)

        evidence_id = record.get("evidence_id")
        if evidence_id not in evidence_ids:
            errors.append(f"Record {index}: unknown evidence_id")

        if record.get("decision") not in ALLOWED_DECISIONS:
            errors.append(f"Record {index}: invalid decision")

        reviewed_at = record.get("reviewed_at")
        if isinstance(reviewed_at, str):
            try:
                parsed = date.fromisoformat(reviewed_at)
                if parsed.isoformat() != reviewed_at:
                    raise ValueError("Noncanonical date")
                if parsed > date.today():
                    errors.append(f"Record {index}: future review date")
            except ValueError:
                errors.append(f"Record {index}: invalid review date")

    return errors


def main():
    reviews = json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))

    evidence_ids = {
        item["evidence_id"]
        for item in evidence
        if isinstance(item, dict)
        and isinstance(item.get("evidence_id"), str)
    }

    errors = validate(reviews, evidence_ids)

    print("YNDR EVIDENCE REVIEW VALIDATION")
    print(f"Reviews: {len(reviews)}")
    print(f"Errors: {len(errors)}")

    for error in errors:
        print("ERROR:", error)

    if errors:
        sys.exit(1)

    print("EVIDENCE REVIEW VALIDATION: PASS")


if __name__ == "__main__":
    main()
