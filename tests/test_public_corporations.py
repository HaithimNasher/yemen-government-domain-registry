import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/registry.db"
DATA = ROOT / "data/public_corporations.json"


class TestPublicCorporations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(
            DATA.read_text(encoding="utf-8")
        )
        cls.conn = sqlite3.connect(DB)
        cls.conn.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_record_count(self):
        self.assertEqual(len(self.records), 16)

    def test_unique_identifiers_and_domains(self):
        ids = [r["entity_id"] for r in self.records]
        domains = [r["domain"] for r in self.records]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(domains), len(set(domains)))

    def test_records_exist_in_database(self):
        for record in self.records:
            with self.subTest(entity=record["entity_id"]):
                row = self.conn.execute(
                    """
                    SELECT * FROM entities
                    WHERE entity_id = ?
                    """,
                    (record["entity_id"],)
                ).fetchone()

                self.assertIsNotNone(row)
                self.assertEqual(
                    row["domain"], record["domain"]
                )

    def test_domains_are_unverified(self):
        for record in self.records:
            with self.subTest(entity=record["entity_id"]):
                row = self.conn.execute(
                    """
                    SELECT domain_status, ownership_verified
                    FROM entities
                    WHERE entity_id = ?
                    """,
                    (record["entity_id"],)
                ).fetchone()

                self.assertIsNotNone(row)
                self.assertEqual(
                    row["domain_status"], "proposed"
                )
                self.assertEqual(
                    row["ownership_verified"], 0
                )


if __name__ == "__main__":
    unittest.main()
