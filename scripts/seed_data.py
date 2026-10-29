import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

def save(name, records):
    path = DATA / f"{name}.json"
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Prepared {name}: {len(records)} records")

governorates = [
    ("أمانة العاصمة", "Sanaa City", "sanaa-city"),
    ("صنعاء", "Sanaa", "sanaa"),
    ("عدن", "Aden", "aden"),
    ("تعز", "Taiz", "taiz"),
    ("إب", "Ibb", "ibb"),
    ("الحديدة", "Al Hudaydah", "hodeidah"),
    ("حضرموت", "Hadramout", "hadramout"),
    ("ذمار", "Dhamar", "dhamar"),
    ("عمران", "Amran", "amran"),
    ("صعدة", "Saada", "saada"),
    ("حجة", "Hajjah", "hajjah"),
    ("الجوف", "Al Jawf", "aljawf"),
    ("المحويت", "Al Mahwit", "mahweet"),
    ("ريمة", "Raymah", "raymah"),
    ("البيضاء", "Al Bayda", "albayda"),
    ("مأرب", "Marib", "marib"),
    ("شبوة", "Shabwah", "shabwah"),
    ("أبين", "Abyan", "abyan"),
    ("لحج", "Lahj", "lahj"),
    ("الضالع", "Al Dhale", "aldhale"),
    ("المهرة", "Al Mahrah", "almahrah"),
    ("سقطرى", "Socotra", "socotra")
]

records = []
for index, (ar, en, slug) in enumerate(governorates, 1):
    records.append({
        "entity_id": f"YE-GOV-{index:03d}",
        "name_ar": ar,
        "name_en": en,
        "category": "governorate",
        "parent_entity_id": None,
        "domain": f"{slug}.gov.ye",
        "domain_status": "proposed",
        "ownership_verified": False,
        "source_url": None,
        "last_verified": None
    })

save("governorates", records)

national = [
    {"suffix": ".ye", "category": "national"},
    {"suffix": ".gov.ye", "category": "government"},
    {"suffix": ".edu.ye", "category": "education"},
    {"suffix": ".com.ye", "category": "commercial"},
    {"suffix": ".org.ye", "category": "organizations"},
    {"suffix": ".net.ye", "category": "network"},
    {"suffix": ".sch.ye", "category": "schools"},
    {"suffix": ".med.ye", "category": "medical"}
]
save("national_domains", national)

for category in [
    "ministries", "districts", "universities",
    "companies", "organizations"
]:
    path = DATA / f"{category}.json"
    if not path.exists():
        save(category, [])

print("Seed files ready.")
