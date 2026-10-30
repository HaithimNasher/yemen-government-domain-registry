import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_FILE = ROOT / "data/evidence/institutions.json"


def get_evidence(entity_id=None):
    records = json.loads(
        EVIDENCE_FILE.read_text(encoding="utf-8")
    )

    if entity_id is not None:
        records = [
            item for item in records
            if item.get("entity_id") == entity_id
        ]

    return {
        "total": len(records),
        "results": records
    }
