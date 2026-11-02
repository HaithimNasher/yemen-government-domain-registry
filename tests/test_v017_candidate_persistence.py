import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import add_source_candidate as module


class CandidatePersistenceTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        governance = self.root / "data/governance"
        governance.mkdir(parents=True)

        self.reviews = governance / "source_reviews.json"
        self.candidates = governance / "source_candidates.json"

        self.reviews.write_text(json.dumps([{
            "entity_id": "YE-TEST-001",
            "source_file": "universities.json",
            "verification_status": "unverified",
        }]), encoding="utf-8")

        self.candidates.write_text(json.dumps({
            "version": "0.17.0",
            "records": [],
        }), encoding="utf-8")

    def add_candidate(self, url):
        argv = [
            "add_source_candidate.py",
            "--entity-id", "YE-TEST-001",
            "--url", url,
            "--notes", "Evidence requires review",
        ]

        with patch.object(module, "ROOT", self.root), \
             patch.object(module, "QUEUE", self.candidates), \
             patch.object(sys, "argv", argv):
            module.main()

    def records(self):
        return json.loads(
            self.candidates.read_text(encoding="utf-8")
        )["records"]

    def test_persistent_write(self):
        self.add_candidate("https://example.org/source")

        self.assertEqual(len(self.records()), 1)
        self.assertEqual(
            self.records()[0]["review_status"], "pending"
        )
        self.assertFalse(
            self.records()[0]["ownership_verified"]
        )

    def test_duplicate_rejected(self):
        url = "https://example.org/source"
        self.add_candidate(url)

        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.add_candidate(url)

        self.assertEqual(len(self.records()), 1)

    def test_multiple_distinct_candidates(self):
        self.add_candidate("https://example.org/one")
        self.add_candidate("https://example.org/two")

        self.assertEqual(len(self.records()), 2)

    def test_original_reviews_unchanged(self):
        before = self.reviews.read_bytes()

        self.add_candidate("https://example.org/source")

        self.assertEqual(self.reviews.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
