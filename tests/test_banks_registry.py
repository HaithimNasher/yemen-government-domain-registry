import json
import unittest
from pathlib import Path

from app.registry_search import search_entities

ROOT = Path(__file__).resolve().parent.parent


class TestBanksRegistry(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.banks = json.loads(
            (ROOT / "data/banks_candidates.json").read_text(
                encoding="utf-8"
            )
        )

    def test_count(self):
        self.assertEqual(len(self.banks), 33)

    def test_unique_ids(self):
        ids = [b["entity_id"] for b in self.banks]
        self.assertEqual(len(ids), len(set(ids)))

    def test_unique_domains(self):
        domains = [b["domain"] for b in self.banks]
        self.assertEqual(len(domains), len(set(domains)))

    def test_bank_category(self):
        self.assertTrue(
            all(b["category"] == "bank" for b in self.banks)
        )

    def test_unverified_domains(self):
        for bank in self.banks:
            self.assertFalse(bank["ownership_verified"])
            self.assertEqual(
                bank["domain_status"], "proposed"
            )

    def test_bank_search(self):
        result = search_entities(
            category="bank",
            limit=100
        )
        self.assertEqual(result["total"], 33)


if __name__ == "__main__":
    unittest.main()
