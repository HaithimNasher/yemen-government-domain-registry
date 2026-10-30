import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


class UniversityTests(unittest.TestCase):

    def test_university_records(self):
        records = json.loads(
            (DATA / "universities.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(len(records), 81)

        ids = {r["entity_id"] for r in records}

        self.assertNotIn("YE-UNI-0001", ids)

    def test_database_universities(self):
        with sqlite3.connect(DATA / "registry.db") as db:
            rows = db.execute("""
                SELECT entity_id
                FROM entities
                WHERE category = 'university'
            """).fetchall()

        ids = {row[0] for row in rows}

        self.assertEqual(len(ids), 78)
        self.assertNotIn("YE-UNI-0001", ids)


if __name__ == "__main__":
    unittest.main()
