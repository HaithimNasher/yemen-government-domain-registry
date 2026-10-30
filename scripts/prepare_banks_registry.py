import json
from pathlib import Path

SOURCE = Path("data/governance/banks_import.json")
TARGET = Path("data/banks_candidates.json")

def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = payload["records"]

    assert payload["project"] == "YNDR"
    assert len(records) == payload["count"] == 33

    output = []
    seen_ids = set()
    seen_domains = set()

    for bank in records:
        entity_id = bank["entity_id"]
        domain = bank["proposed_domain"]

        assert entity_id not in seen_ids
        assert domain not in seen_domains
        assert bank["ownership_verified"] is False
        assert bank["license_status"] == "unverified"
        assert bank["official_domain"] is None
        assert bank["domain_status"] == "proposed_unverified"

        seen_ids.add(entity_id)
        seen_domains.add(domain)

        output.append({
            "entity_id": entity_id,
            "name_ar": bank["name_ar"],
            "name_en": bank.get("name_en") or bank["name_ar"],
            "category": "bank",
            "parent_entity_id": None,
            "domain": domain,
            "domain_status": "proposed",
            "ownership_verified": False,
            "source_url": bank.get("source_url"),
            "last_verified": bank.get("last_verified")
        })

    if TARGET.exists():
        raise SystemExit(
            "STOP: Target already exists; refusing to overwrite"
        )

    TARGET.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("YNDR BANK PREPARATION: PASS")
    print("Banks:", len(output))
    print("Output:", TARGET)

if __name__ == "__main__":
    main()
