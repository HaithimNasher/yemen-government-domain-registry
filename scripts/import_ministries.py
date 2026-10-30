import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "data/ministries.json"

source = "https://pmo-ye.net/public/post/11134"

ministries = [
    ("YE-MIN-001", "وزارة الخارجية وشؤون المغتربين",
     "Ministry of Foreign Affairs and Expatriates"),
    ("YE-MIN-002", "وزارة الداخلية",
     "Ministry of Interior"),
    ("YE-MIN-003", "وزارة الدفاع",
     "Ministry of Defense"),
    ("YE-MIN-004", "وزارة المالية",
     "Ministry of Finance"),
    ("YE-MIN-005", "وزارة التربية والتعليم",
     "Ministry of Education"),
    ("YE-MIN-006", "وزارة التعليم العالي والبحث العلمي",
     "Ministry of Higher Education and Scientific Research"),
    ("YE-MIN-007", "وزارة الصحة العامة والسكان",
     "Ministry of Public Health and Population"),
    ("YE-MIN-008", "وزارة الاتصالات وتقنية المعلومات",
     "Ministry of Telecommunications and Information Technology"),
    ("YE-MIN-009", "وزارة العدل",
     "Ministry of Justice"),
    ("YE-MIN-010", "وزارة النقل",
     "Ministry of Transport"),
]

records = json.loads(path.read_text(encoding="utf-8"))
existing = {r["entity_id"] for r in records}

for entity_id, name_ar, name_en in ministries:
    if entity_id in existing:
        continue

    records.append({
        "entity_id": entity_id,
        "name_ar": name_ar,
        "name_en": name_en,
        "category": "ministry",
        "parent_entity_id": None,
        "domain": None,
        "domain_status": "unverified",
        "ownership_verified": False,
        "source_url": source,
        "last_verified": None
    })

path.write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("Ministries:", len(records))
