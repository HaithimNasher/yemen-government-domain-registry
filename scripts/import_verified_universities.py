import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "data/universities.json"
backup = Path.home() / "yndr-backups/universities-before-v0.4.json"

records = json.loads(path.read_text(encoding="utf-8"))

if not backup.exists():
    backup.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

universities = [
    {
        "entity_id": "YE-UNI-SANAA",
        "name_ar": "جامعة صنعاء",
        "name_en": "Sana'a University",
        "domain": "su.edu.ye",
        "source_url": "https://su.edu.ye/"
    },
    {
        "entity_id": "YE-UNI-ADEN",
        "name_ar": "جامعة عدن",
        "name_en": "University of Aden",
        "domain": "ad.edu.ye",
        "source_url": "https://ad.edu.ye/"
    },
    {
        "entity_id": "YE-UNI-UST",
        "name_ar": "جامعة العلوم والتكنولوجيا",
        "name_en": "University of Science and Technology",
        "domain": "ust.edu.ye",
        "source_url": "https://ust.edu.ye/"
    }
]

# Remove only the known example record.
records = [
    r for r in records
    if not (
        r.get("entity_id") == "YE-UNI-0001"
        and r.get("name_en") == "Example University"
    )
]

for university in universities:
    record = {
        **university,
        "category": "university",
        "parent_entity_id": None,
        "domain_status": "observed",
        "ownership_verified": False,
        "last_verified": None
    }

    matches = [
        r for r in records
        if r.get("entity_id") == record["entity_id"]
        or r.get("domain") == record["domain"]
    ]

    if len(matches) > 1:
        raise SystemExit(
            "Conflicting university records: "
            + record["entity_id"]
        )

    if matches:
        matches[0].update(record)
    else:
        records.append(record)

path.write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("Universities:", len(records))
print("Import completed.")
