"""Collect pending source evidence for YNDR governance."""

import argparse
import fcntl
import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

from .add_source_candidate import validate_url
from . import validate_evidence_registry as validator


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance/evidence_registry.json"

ALLOWED_INTAKE_TYPES = {
    "entity_existence",
    "official_website",
    "domain_observation",
}


def nonempty(value):
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError(
            "Value must not be empty"
        )
    return value


def collect(
    entity_id,
    source_url,
    evidence_type,
    discovered_from,
    notes,
    source_candidate_url=None,
):
    if evidence_type not in ALLOWED_INTAKE_TYPES:
        raise ValueError("Unsupported intake evidence type")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (
            entity_id,
            source_url,
            discovered_from,
            notes,
        )
    ):
        raise ValueError("Required metadata is missing")

    validate_url(source_url)

    if source_candidate_url is not None:
        validate_url(source_candidate_url)

    if entity_id not in validator.load_entity_ids():
        raise ValueError(f"Unknown entity: {entity_id}")

    REGISTRY.parent.mkdir(parents=True, exist_ok=True)

    lock_path = REGISTRY.with_name(
        REGISTRY.name + ".lock"
    )

    candidate_lock_path = (
        ROOT / "data/governance/source_candidates.json.lock"
    )

    if source_candidate_url is not None:
        candidate_lock_path.parent.mkdir(
            parents=True, exist_ok=True
        )
        candidate_lock = candidate_lock_path.open("a+")
        fcntl.flock(candidate_lock.fileno(), fcntl.LOCK_EX)
    else:
        candidate_lock = None

    try:
        return _collect_locked(
            entity_id,
            source_url,
            evidence_type,
            discovered_from,
            notes,
            source_candidate_url,
            lock_path,
        )
    finally:
        if candidate_lock is not None:
            fcntl.flock(candidate_lock.fileno(), fcntl.LOCK_UN)
            candidate_lock.close()


def _collect_locked(
    entity_id,
    source_url,
    evidence_type,
    discovered_from,
    notes,
    source_candidate_url,
    lock_path,
):
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        records = json.loads(
            REGISTRY.read_text(encoding="utf-8")
        )

        if source_candidate_url is not None:
            candidate_path = (
                ROOT / "data/governance/source_candidates.json"
            )

            candidate_data = json.loads(
                candidate_path.read_text(encoding="utf-8")
            )

            if not isinstance(candidate_data, dict):
                raise ValueError("Invalid candidate registry")

            candidates = candidate_data.get("records")

            if not isinstance(candidates, list):
                raise ValueError("Invalid candidate records")

            matched = any(
                isinstance(item, dict)
                and item.get("entity_id") == entity_id
                and item.get("candidate_source_url")
                == source_candidate_url
                and item.get("ownership_verified") is False
                and item.get("review_status") == "pending"
                for item in candidates
            )

            if not matched:
                raise ValueError(
                    "Pending source candidate not found for entity"
                )

        if not isinstance(records, list):
            raise ValueError(
                "Evidence registry must be a list"
            )

        existing_errors = validator.validate(records)
        if existing_errors:
            raise ValueError(
                "Existing registry is invalid: "
                + "; ".join(existing_errors[:3])
            )

        normalized_url = source_url.strip()

        for record in records:
            if (
                record.get("entity_id") == entity_id
                and record.get("evidence_type")
                == evidence_type
                and record.get("source_url")
                == normalized_url
            ):
                raise ValueError(
                    "Duplicate evidence for entity, "
                    "type and URL"
                )

        record = {
            "evidence_id": "EV-" + uuid.uuid4().hex[:16].upper(),
            "entity_id": entity_id,
            "evidence_type": evidence_type,
            "source_url": normalized_url,
            "verification_status": "pending",
            "collected_at": date.today().isoformat(),
            "discovered_from": discovered_from.strip(),
            "collection_notes": notes.strip(),
            "reviewed_at": None,
            "review_notes": None,
        }

        if source_candidate_url is not None:
            record["source_candidate_url"] = (
                source_candidate_url
            )

        updated = records + [record]
        errors = validator.validate(updated)

        if errors:
            raise ValueError(
                "Evidence validation failed: "
                + "; ".join(errors[:3])
            )

        temporary = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=REGISTRY.parent,
                prefix=".evidence-",
                suffix=".tmp",
                delete=False,
            ) as output:
                temporary = Path(output.name)
                json.dump(
                    updated,
                    output,
                    ensure_ascii=False,
                    indent=2,
                )
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())

            os.replace(temporary, REGISTRY)
            temporary = None

        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        return record


def main():
    parser = argparse.ArgumentParser(
        description="Collect pending YNDR source evidence"
    )

    parser.add_argument(
        "--entity-id", required=True, type=nonempty
    )
    parser.add_argument(
        "--url", required=True, type=nonempty
    )
    parser.add_argument(
        "--evidence-type",
        required=True,
        choices=sorted(ALLOWED_INTAKE_TYPES),
    )
    parser.add_argument(
        "--discovered-from",
        required=True,
        type=nonempty,
    )
    parser.add_argument(
        "--notes", required=True, type=nonempty
    )

    parser.add_argument(
        "--source-candidate-url",
        default=None,
        help="Optional previously registered source candidate URL",
    )

    args = parser.parse_args()

    try:
        record = collect(
            args.entity_id,
            args.url,
            args.evidence_type,
            args.discovered_from,
            args.notes,
            source_candidate_url=args.source_candidate_url,
        )
    except ValueError as exc:
        parser.error(str(exc))

    print("SOURCE EVIDENCE COLLECTED")
    print("Evidence:", record["evidence_id"])
    print("Entity:", record["entity_id"])
    print("Status:", record["verification_status"])
    print("Ownership verified: NO")


if __name__ == "__main__":
    main()
