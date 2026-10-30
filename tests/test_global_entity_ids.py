import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

ENTITY_FILES = [
    "ministries.json",
    "governorates.json",
    "districts.json",
    "universities.json",
    "companies.json",
    "organizations.json",
    "government_services.json",
]


class GlobalEntityIDTests(unittest.TestCase):

    def test_unique_entity_ids_across_all_files(self):
        ids = []

        for filename in ENTITY_FILES:
            path = DATA / filename
            if not path.exists():
                continue

            records = json.loads(
                path.read_text(encoding="utf-8")
            )

            ids.extend(
                record["entity_id"]
                for record in records
            )

        duplicates = [
            entity_id
            for entity_id, count in Counter(ids).items()
            if count > 1
        ]

        self.assertEqual(
            duplicates, [],
            f"Duplicate entity IDs: {duplicates}"
        )

    def test_governorate_ids_not_used_by_institutions(self):
        path = DATA / "government_services.json"

        records = json.loads(
            path.read_text(encoding="utf-8")
        )

        for record in records:
            self.assertFalse(
                record["entity_id"].startswith("YE-GOV-"),
                f"Reserved governorate ID: {record['entity_id']}"
            )


if __name__ == "__main__":
    unittest.main()
