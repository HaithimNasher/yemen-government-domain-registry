import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


class DistrictRegistryTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.districts = json.loads(
            (DATA / "districts.json").read_text(
                encoding="utf-8"
            )
        )
        cls.governorates = json.loads(
            (DATA / "governorates.json").read_text(
                encoding="utf-8"
            )
        )

    def test_district_count(self):
        self.assertEqual(len(self.districts), 335)

    def test_governorate_count(self):
        self.assertEqual(len(self.governorates), 22)

    def test_unique_entity_ids(self):
        ids = [r["entity_id"] for r in self.districts]
        self.assertEqual(len(ids), len(set(ids)))

    def test_unique_domains(self):
        domains = [r["domain"] for r in self.districts]
        self.assertEqual(len(domains), len(set(domains)))

    def test_valid_parents(self):
        valid_ids = {
            r["entity_id"] for r in self.governorates
        }

        for district in self.districts:
            self.assertIn(
                district["parent_entity_id"],
                valid_ids
            )

    def test_no_claimed_ownership(self):
        for district in self.districts:
            self.assertFalse(
                district["ownership_verified"]
            )
            self.assertEqual(
                district["domain_status"],
                "proposed"
            )

    def test_database(self):
        with sqlite3.connect(DATA / "registry.db") as db:
            count = db.execute("""
                SELECT COUNT(*)
                FROM entities
                WHERE category = 'district'
            """).fetchone()[0]

        self.assertEqual(count, 335)


if __name__ == "__main__":
    unittest.main()
