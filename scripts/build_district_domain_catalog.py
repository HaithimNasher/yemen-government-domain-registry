import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

districts = json.loads(
    (DATA / "districts.json").read_text(encoding="utf-8")
)
governorates = json.loads(
    (DATA / "governorates.json").read_text(encoding="utf-8")
)

assert len(districts) == 335, "Unexpected district count"

gov_by_id = {g["entity_id"]: g for g in governorates}
assert len(gov_by_id) == len(governorates)

def validate_domain(domain):
    if not isinstance(domain, str):
        raise ValueError("Domain must be a string")
    if len(domain) > 253:
        raise ValueError(f"Domain too long: {domain}")
    labels = domain.split(".")
    for label in labels:
        if not re.fullmatch(
            r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?",
            label
        ):
            raise ValueError(f"Invalid domain: {domain}")

def short_slug(domain, gov_domain):
    suffix = "." + gov_domain
    if not domain.endswith(suffix):
        raise ValueError(f"Wrong governorate: {domain}")

    label = domain[:-len(suffix)]
    if "." in label:
        raise ValueError(f"Unexpected district label: {domain}")

    # Existing district domains end with their administrative code.
    match = re.fullmatch(r"(.+)-ye[0-9]{4}", label)
    if not match:
        raise ValueError(f"Unexpected domain pattern: {domain}")

    return match.group(1)

catalog = []

for district in districts:
    gov_id = district["parent_entity_id"]
    if gov_id not in gov_by_id:
        raise ValueError(
            f"Missing governorate for {district['entity_id']}"
        )

    gov = gov_by_id[gov_id]
    gov_domain = gov.get("domain")
    primary = district.get("domain")

    if not gov_domain or not primary:
        raise ValueError(
            f"Missing domain: {district['entity_id']}"
        )

    if district.get("domain_status") != "proposed":
        raise ValueError(
            f"Unexpected district status: {district['entity_id']}"
        )

    if district.get("ownership_verified") is not False:
        raise ValueError(
            f"Unexpected ownership state: {district['entity_id']}"
        )

    validate_domain(gov_domain)
    validate_domain(primary)

    slug = short_slug(primary, gov_domain)
    alias = f"{slug}.{gov_domain}"
    validate_domain(alias)

    catalog.append({
        "entity_id": district["entity_id"],
        "name_ar": district["name_ar"],
        "name_en": district["name_en"],
        "governorate_entity_id": gov_id,
        "governorate_name_ar": gov["name_ar"],
        "primary_domain": primary,
        "proposed_alias": alias,
        "alias_status": "proposed",
        "ownership_verified": False,
        "source_url": None,
        "last_verified": None
    })

all_primary = [
    r["primary_domain"] for r in catalog
]
all_aliases = [
    r["proposed_alias"] for r in catalog
]

for label, values in [
    ("Primary domains", all_primary),
    ("Proposed aliases", all_aliases),
]:
    duplicates = [
        value for value, count in Counter(values).items()
        if count > 1
    ]
    if duplicates:
        raise ValueError(
            f"{label} have duplicates: {duplicates}"
        )

if set(all_primary) & set(all_aliases):
    raise ValueError("Primary/alias collision")

# Check against existing primary domains across the registry.
for path in DATA.glob("*.json"):
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        continue

    for record in records:
        if not isinstance(record, dict):
            continue
        domain = record.get("domain")
        if not domain:
            continue

        if (
            path.name != "districts.json"
            and domain in set(all_aliases)
        ):
            raise ValueError(
                f"Alias conflicts with {path}: {domain}"
            )

catalog.sort(key=lambda r: r["entity_id"])

output = DATA / "governance" / "district_domain_catalog.json"
output.parent.mkdir(parents=True, exist_ok=True)

content = json.dumps(
    catalog, ensure_ascii=False, indent=2
) + "\n"

if output.exists():
    existing = output.read_text(encoding="utf-8")
    if existing != content:
        raise SystemExit(
            "Existing catalog differs. Review before overwriting."
        )
else:
    output.write_text(content, encoding="utf-8")

print("YNDR DISTRICT DOMAIN CATALOG")
print("Districts:", len(catalog))
print("Primary domains:", len(all_primary))
print("Proposed aliases:", len(all_aliases))
print("Duplicate domains: 0")
print("Ownership verified: 0")
print("Output:", output)
print("PASS")
