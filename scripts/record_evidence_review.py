"""Register governed evidence review decisions."""

import argparse
import fcntl
import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

from .validate_evidence_registry import validate as validate_evidence
from .validate_review_transitions import validate_transitions
from .validate_evidence_reviews import ALLOWED_DECISIONS


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data/governance/evidence_registry.json"
REVIEWS_PATH = ROOT / "data/governance/evidence_reviews.json"


def required(value):
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("Value cannot be empty")
    return value


def atomic_write(path, records):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".review-",
            suffix=".tmp",
            delete=False,
        ) as output:
            temporary = Path(output.name)
            json.dump(
                records, output,
                ensure_ascii=False, indent=2,
            )
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())

        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def record_review(
    evidence_id,
    reviewer_id,
    decision,
    notes,
):
    if decision not in ALLOWED_DECISIONS:
        raise ValueError("Invalid review decision")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (evidence_id, reviewer_id, notes)
    ):
        raise ValueError("Missing required review metadata")

    REVIEWS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Lock order: evidence first, reviews second.
    evidence_lock = EVIDENCE_PATH.with_name(
        EVIDENCE_PATH.name + ".lock"
    )
    review_lock = REVIEWS_PATH.with_name(
        REVIEWS_PATH.name + ".lock"
    )

    with evidence_lock.open("a+") as source_lock:
        fcntl.flock(source_lock.fileno(), fcntl.LOCK_EX)

        with review_lock.open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

            evidence = json.loads(
                EVIDENCE_PATH.read_text(encoding="utf-8")
            )
            reviews = json.loads(
                REVIEWS_PATH.read_text(encoding="utf-8")
            )

            if not isinstance(evidence, list):
                raise ValueError("Invalid evidence registry")

            if not isinstance(reviews, list):
                raise ValueError("Invalid review registry")

            evidence_errors = validate_evidence(evidence)
            if evidence_errors:
                raise ValueError(
                    "Evidence registry invalid: "
                    + "; ".join(evidence_errors[:3])
                )

            evidence_ids = {
                item["evidence_id"]
                for item in evidence
            }

            if evidence_id not in evidence_ids:
                raise ValueError(
                    f"Unknown evidence_id: {evidence_id}"
                )

            existing_errors = validate_transitions(
                reviews, evidence_ids
            )
            if existing_errors:
                raise ValueError(
                    "Existing review history invalid: "
                    + "; ".join(existing_errors[:3])
                )

            today = date.today().isoformat()

            # A reviewer cannot submit the same decision
            # twice for the same evidence on the same day.
            for item in reviews:
                if (
                    item["evidence_id"] == evidence_id
                    and item["reviewer_id"] == reviewer_id
                    and item["reviewed_at"] == today
                    and item["decision"] == decision
                ):
                    raise ValueError(
                        "Duplicate reviewer decision"
                    )

            record = {
                "review_id": (
                    "REV-" + uuid.uuid4().hex[:16].upper()
                ),
                "evidence_id": evidence_id,
                "reviewer_id": reviewer_id.strip(),
                "decision": decision,
                "reviewed_at": today,
                "review_notes": notes.strip(),
            }

            updated = reviews + [record]
            errors = validate_transitions(
                updated, evidence_ids
            )

            if errors:
                raise ValueError(
                    "Review transition rejected: "
                    + "; ".join(errors[:3])
                )

            atomic_write(REVIEWS_PATH, updated)
            return record


def main():
    parser = argparse.ArgumentParser(
        description="Register a YNDR evidence review"
    )
    parser.add_argument(
        "--evidence-id", required=True, type=required
    )
    parser.add_argument(
        "--reviewer-id", required=True, type=required
    )
    parser.add_argument(
        "--decision",
        required=True,
        choices=sorted(ALLOWED_DECISIONS),
    )
    parser.add_argument(
        "--notes", required=True, type=required
    )

    args = parser.parse_args()

    try:
        record = record_review(
            args.evidence_id,
            args.reviewer_id,
            args.decision,
            args.notes,
        )
    except ValueError as exc:
        parser.error(str(exc))

    print("EVIDENCE REVIEW RECORDED")
    print("Review:", record["review_id"])
    print("Evidence:", record["evidence_id"])
    print("Decision:", record["decision"])
    print("Ownership verified: NO")


if __name__ == "__main__":
    main()
