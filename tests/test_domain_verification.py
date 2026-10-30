import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "governorates.json",
    "districts.json",
    "ministries.json",
    "universities.json",
    "government_services.json",
]


class DomainVerificationTests(unittest.TestCase):

    def test_ownership_flags_are_boolean(self):
        for filename in FILES:
            path = ROOT / "data" / filename
            records = json.loads(
                path.read_text(encoding="utf-8")
            )

            for record in records:
                if "ownership_verified" in record:
                    self.assertIsInstance(
                        record["ownership_verified"],
                        bool
                    )

    def test_proposed_domains_not_verified(self):
        for filename in FILES:
            path = ROOT / "data" / filename
            records = json.loads(
                path.read_text(encoding="utf-8")
            )

            for record in records:
                if record.get("domain_status") == "proposed":
                    self.assertIsNot(
                        record.get("ownership_verified"),
                        True,
                        msg=record["entity_id"]
                    )


if __name__ == "__main__":
    unittest.main()
