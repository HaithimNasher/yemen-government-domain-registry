import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EVIDENCE = ROOT / "data/evidence/institutions.json"
DATABASE = ROOT / "data/registry.db"


def main():
    evidence = json.loads(
        EVIDENCE.read_text(encoding="utf-8")
    )

    if not isinstance(evidence, list):
        print("ERROR: Evidence must be a JSON array")
        return 1

    with sqlite3.connect(DATABASE) as conn:
        rows = conn.execute(
            "SELECT entity_id, domain FROM entities"
        ).fetchall()

    entities = {
        entity_id: domain
        for entity_id, domain in rows
    }

    errors = []
    seen = set()

    for item in evidence:
        entity_id = item.get("entity_id")
        domain = item.get("domain")

        if not entity_id or entity_id not in entities:
            errors.append(
                f"Unknown entity: {entity_id}"
            )
            continue

        if entity_id in seen:
            errors.append(
                f"Duplicate evidence: {entity_id}"
            )

        seen.add(entity_id)

        registered_domain = entities[entity_id]

        if domain != registered_domain:
            errors.append(
                f"Domain mismatch: {entity_id}"
            )

        if item.get("ownership_verified") is not False:
            errors.append(
                f"Unsubstantiated ownership: {entity_id}"
            )

        if item.get("review_status") != "pending":
            errors.append(
                f"Unexpected review status: {entity_id}"
            )

    print("YNDR EVIDENCE VALIDATION")
    print("Evidence records:", len(evidence))
    print("Errors:", len(errors))

    for error in errors:
        print("ERROR:", error)

    if errors:
        return 1

    print("EVIDENCE VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
