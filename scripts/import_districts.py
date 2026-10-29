import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

source_path = DATA / "sources/yemen-districts-source.json"
districts_path = DATA / "districts.json"
governorates_path = DATA / "governorates.json"

source = json.loads(source_path.read_text(encoding="utf-8"))
governorates = json.loads(
    governorates_path.read_text(encoding="utf-8")
)

if len(source) != 335:
    raise SystemExit("Expected 335 source districts")

# Map source governorate IDs to registry governorates.
# Explicit mapping avoids ambiguous name matching.
parent_map = {
    "YE17": "hajjah",
    "YE30": "aldhale",
    "YE19": "hadramout",
    "YE18": "hodeidah",
    "YE13": "sanaa-city",
    "YE15": "taiz",
    "YE22": "saada",
    "YE26": "marib",
    "YE28": "almahrah"
}

registry_by_slug = {
    r["domain"].split(".")[0]: r
    for r in governorates
}

# Expand mapping from exact normalized English names
# only when the match is unambiguous.
aliases = {
    "hajjah": "hajjah",
    "ad dali": "aldhale",
    "hadramawt": "hadramout",
    "al hodeidah": "hodeidah",
    "sanaa": "sanaa",
    "sana a": "sanaa",
    "aden": "aden",
    "taiz": "taiz",
    "ibb": "ibb",
    "dhamar": "dhamar",
    "amran": "amran",
    "saada": "saada",
    "al jawf": "aljawf",
    "al mahwit": "mahweet",
    "raymah": "raymah",
    "al bayda": "albayda",
    "marib": "marib",
    "shabwah": "shabwah",
    "abyan": "abyan",
    "lahj": "lahj",
    "al mahrah": "almahrah",
    "socotra": "socotra"
}

def normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

# Resolve every parent before writing output.
unresolved = {}
for district in source:
    parent = district["parent"]
    parent_id = parent["id"]
    if parent_id in parent_map:
        continue

    name = normalize(parent["name"]["en"])
    slug = aliases.get(name)

    if slug and slug in registry_by_slug:
        parent_map[parent_id] = slug
    else:
        unresolved[parent_id] = parent["name"]["en"]

if unresolved:
    print("Unresolved governorates:")
    for parent_id, name in sorted(unresolved.items()):
        print(parent_id, name)
    raise SystemExit(
        "Import stopped. Review governorate mapping."
    )

records = []
seen_ids = set()
seen_domains = set()

for district in source:
    source_id = district["id"]
    parent_id = district["parent"]["id"]
    governorate_slug = parent_map[parent_id]
    governorate = registry_by_slug[governorate_slug]

    name = district["name"]
    base_slug = name["slug"]

    # The source slug includes a unique source identifier.
    safe_slug = re.sub(
        r"[^a-z0-9-]", "",
        base_slug.lower()
    ).strip("-")

    domain = (
        f"{safe_slug}.{governorate_slug}.gov.ye"
    )

    record = {
        "entity_id": f"YE-DIST-{source_id}",
        "name_ar": name["local"],
        "name_en": name["en"],
        "category": "district",
        "parent_entity_id": governorate["entity_id"],
        "domain": domain,
        "domain_status": "proposed",
        "ownership_verified": False,
        "source_url": (
            "https://github.com/open-admin-data/"
            "yemen-administrative-divisions"
        ),
        "last_verified": None
    }

    if record["entity_id"] in seen_ids:
        raise ValueError("Duplicate entity ID")

    if domain in seen_domains:
        raise ValueError("Duplicate domain")

    seen_ids.add(record["entity_id"])
    seen_domains.add(domain)
    records.append(record)

if len(records) != 335:
    raise ValueError("Incorrect district count")

districts_path.write_text(
    json.dumps(records, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Districts imported:", len(records))
print("Governorates mapped:", len(parent_map))
print("Unique domains:", len(seen_domains))
print("Output:", districts_path)
