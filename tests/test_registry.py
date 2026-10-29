import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "registry.db"

class RegistryTests(unittest.TestCase):
    def test_database_exists(self):
        self.assertTrue(DB.exists())

    def test_governorates_count(self):
        with sqlite3.connect(DB) as db:
            total = db.execute("""
                SELECT COUNT(*) FROM entities
                WHERE category = 'governorate'
            """).fetchone()[0]
        self.assertEqual(total, 22)

    def test_no_verified_proposals(self):
        with sqlite3.connect(DB) as db:
            total = db.execute("""
                SELECT COUNT(*) FROM entities
                WHERE domain_status = 'proposed'
                  AND ownership_verified = 1
            """).fetchone()[0]
        self.assertEqual(total, 0)

if __name__ == "__main__":
    unittest.main()
