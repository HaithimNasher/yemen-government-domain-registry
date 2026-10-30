import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/governance/evidence_registry.json"

ALLOWED_TYPES = {
    "entity_existence",
    "official_website",
    "domain_observation",
    "domain_ownership",
}

ALLOWED_STATUSES = {
    "pending",
    "under_review",
    "verified",
    "rejected",
}

def load_entity_ids():
    files = [
        "governorates.json",
        "districts.json",
        "ministries.json",
        "universities.json",
        "government_services.json",
    ]

    entity_ids = set()

    for filename in files:
        source = ROOT / "data" / filename
        records = json.loads(source.read_text(encoding="utf-8"))

        for record in records:
            entity_id = record.get("entity_id")
            if isinstance(entity_id, str) and entity_id:
                entity_ids.add(entity_id)

    return entity_ids


def load_entity_domains():
    files = [
        "governorates.json",
        "districts.json",
        "ministries.json",
        "universities.json",
        "government_services.json",
    ]

    domains = {}

    for filename in files:
        source = ROOT / "data" / filename
        records = json.loads(source.read_text(encoding="utf-8"))

        for record in records:
            entity_id = record.get("entity_id")
            domain = record.get("domain")

            if entity_id and domain:
                domains[entity_id] = domain.lower().rstrip(".")

    return domains


def validate(records):
    errors = []
    ids = set()

    if not isinstance(records, list):
        return ["Evidence registry must be a list"]

    valid_entity_ids = load_entity_ids()
    entity_domains = load_entity_domains()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"Record {index}: not an object")
            continue

        evidence_id = record.get("evidence_id")
        entity_id = record.get("entity_id")
        evidence_type = record.get("evidence_type")
        status = record.get("verification_status")
        url = record.get("source_url")

        if not isinstance(evidence_id, str) or not evidence_id.strip():
            errors.append(f"Record {index}: missing evidence_id")
        elif evidence_id in ids:
            errors.append(f"Duplicate evidence_id: {evidence_id}")
        else:
            ids.add(evidence_id)

        if not isinstance(entity_id, str) or not entity_id.strip():
            errors.append(f"Record {index}: missing entity_id")
        elif entity_id not in valid_entity_ids:
            errors.append(f"Record {index}: unknown entity_id: {entity_id}")

        if evidence_type not in ALLOWED_TYPES:
            errors.append(f"Record {index}: invalid evidence_type")

        if status not in ALLOWED_STATUSES:
            errors.append(f"Record {index}: invalid status")

        if url is not None:
            if not isinstance(url, str):
                errors.append(f"Record {index}: invalid source_url")
            else:
                parsed = urlparse(url)
                if parsed.scheme not in ("http", "https") or not parsed.netloc:
                    errors.append(f"Record {index}: invalid source_url")

        if evidence_type == "domain_ownership":
            claimed_domain = record.get("domain")
            expected_domain = entity_domains.get(entity_id)

            if isinstance(claimed_domain, str) and claimed_domain.strip():
                normalized = claimed_domain.strip().lower().rstrip(".")

                if expected_domain is None:
                    errors.append(
                        f"Record {index}: entity has no registered domain"
                    )
                elif normalized != expected_domain:
                    errors.append(
                        f"Record {index}: domain does not match entity"
                    )


            required_fields = (
                "domain",
                "verification_method",
                "evidence_reference",
                "reviewed_by",
            )

            for field in required_fields:
                value = record.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        f"Record {index}: domain ownership "
                        f"missing {field}"
                    )

        if (
            evidence_type == "domain_ownership"
            and status == "verified"
        ):
            errors.append(
                f"Record {index}: domain ownership requires "
                "independent verification workflow"
            )

        if status == "verified":
            if not url:
                errors.append(f"Record {index}: verified without source")
            reviewed_at = record.get("reviewed_at")
            if not isinstance(reviewed_at, str) or not reviewed_at.strip():
                errors.append(f"Record {index}: verified without review date")
            else:
                try:
                    parsed_date = date.fromisoformat(reviewed_at)
                    if parsed_date.isoformat() != reviewed_at:
                        raise ValueError("Non-canonical date")
                    if parsed_date > date.today():
                        errors.append(f"Record {index}: future review date")
                except ValueError:
                    errors.append(f"Record {index}: invalid review date")

            notes = record.get("review_notes")
            if not isinstance(notes, str) or not notes.strip():
                errors.append(f"Record {index}: verified without review notes")

    return errors

def main():
    records = json.loads(PATH.read_text(encoding="utf-8"))
    errors = validate(records)

    print("YNDR EVIDENCE REGISTRY VALIDATION")
    print("Records:", len(records) if isinstance(records, list) else "invalid")
    print("Errors:", len(errors))

    for error in errors:
        print("ERROR:", error)

    if errors:
        raise SystemExit(1)

    print("EVIDENCE REGISTRY VALIDATION: PASS")

if __name__ == "__main__":
    main()
