import argparse
import json
import socket
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FILES = [
    "ministries.json",
    "universities.json",
    "companies.json",
    "organizations.json",
]


def check_domain(domain):
    try:
        results = socket.getaddrinfo(
            domain,
            None,
            type=socket.SOCK_STREAM
        )

        addresses = sorted({
            item[4][0] for item in results
        })

        return {
            "dns_status": "resolved",
            "addresses": addresses
        }

    except socket.gaierror as exc:
        return {
            "dns_status": "unresolved",
            "addresses": [],
            "error": str(exc)
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live",
        action="store_true",
        help="Perform live DNS lookups"
    )
    args = parser.parse_args()

    results = []

    for filename in FILES:
        path = DATA / filename

        if not path.exists():
            continue

        records = json.loads(
            path.read_text(encoding="utf-8")
        )

        for record in records:
            domain = record.get("domain")

            if not domain:
                continue

            item = {
                "entity_id": record.get("entity_id"),
                "name_ar": record.get("name_ar"),
                "domain": domain,
                "ownership_verified": False
            }

            if args.live:
                item.update(check_domain(domain))
            else:
                item["dns_status"] = "not_checked"
                item["addresses"] = []

            results.append(item)

    report = {
        "project": "YNDR",
        "verification_type": "DNS",
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "live_checks": args.live,
        "results": results
    }

    output = ROOT / "domain-dns-report.json"

    output.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2
        ) + "\n",
        encoding="utf-8"
    )

    print("YNDR DOMAIN DNS CHECK")
    print("Domains:", len(results))

    for item in results:
        print(
            item["entity_id"],
            item["domain"],
            item["dns_status"]
        )

    print("Report:", output)


if __name__ == "__main__":
    main()
