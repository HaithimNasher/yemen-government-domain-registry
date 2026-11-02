import json
import tempfile
import unittest
from pathlib import Path

from scripts.record_source_decision import record_decision


class RecordSourceDecisionTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        root = Path(self.temp.name)

        self.decisions_path = root / "decisions.json"
        self.candidates_path = root / "candidates.json"
        self.reviews_path = root / "reviews.json"

        self.entity_id = "YE-TEST-001"
        self.url = "https://example.org/source"

        self.write_json(self.decisions_path, {
            "version": "0.18.0",
            "records": [],
        })

        self.write_json(self.candidates_path, {
            "version": "0.17.0",
            "records": [{
                "entity_id": self.entity_id,
                "candidate_source_url": self.url,
                "review_status": "pending",
                "ownership_verified": False,
            }],
        })

        self.write_json(self.reviews_path, [{
            "entity_id": self.entity_id,
            "verification_status": "unverified",
            "source_url": None,
            "verified_at": None,
        }])

    @staticmethod
    def write_json(path, data):
        path.write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )

    def submit(self, **overrides):
        args = {
            "entity_id": self.entity_id,
            "url": self.url,
            "decision": "accepted",
            "reviewer": "Test Reviewer",
            "notes": "Manual test review",
            "decisions_path": self.decisions_path,
            "candidates_path": self.candidates_path,
            "reviews_path": self.reviews_path,
        }
        args.update(overrides)
        return record_decision(**args)

    def read_decisions(self):
        return json.loads(
            self.decisions_path.read_text(encoding="utf-8")
        )["records"]

    def test_records_valid_decision(self):
        record = self.submit()

        self.assertEqual(record["decision"], "accepted")
        self.assertFalse(record["ownership_verified"])
        self.assertEqual(len(self.read_decisions()), 1)

    def test_rejects_duplicate_candidate_decision(self):
        self.submit()

        before = self.decisions_path.read_bytes()

        with self.assertRaises(ValueError):
            self.submit(decision="rejected")

        self.assertEqual(
            self.decisions_path.read_bytes(),
            before,
        )

    def test_rejects_unknown_candidate(self):
        before = self.decisions_path.read_bytes()

        with self.assertRaises(ValueError):
            self.submit(url="https://example.org/unknown")

        self.assertEqual(
            self.decisions_path.read_bytes(),
            before,
        )

    def test_rejects_missing_reviewer(self):
        with self.assertRaises(ValueError):
            self.submit(reviewer="")

        self.assertEqual(self.read_decisions(), [])

    def test_rejects_missing_notes(self):
        with self.assertRaises(ValueError):
            self.submit(notes="")

        self.assertEqual(self.read_decisions(), [])

    def test_rejects_invalid_decision(self):
        with self.assertRaises(ValueError):
            self.submit(decision="verified_automatically")

        self.assertEqual(self.read_decisions(), [])

    def test_preserves_candidate_and_review_files(self):
        before_candidates = self.candidates_path.read_bytes()
        before_reviews = self.reviews_path.read_bytes()

        self.submit()

        self.assertEqual(
            self.candidates_path.read_bytes(),
            before_candidates,
        )
        self.assertEqual(
            self.reviews_path.read_bytes(),
            before_reviews,
        )

    def test_rejects_invalid_existing_registry(self):
        self.write_json(self.decisions_path, {
            "version": "0.18.0",
            "records": [{"invalid": True}],
        })

        before = self.decisions_path.read_bytes()

        with self.assertRaises(ValueError):
            self.submit()

        self.assertEqual(
            self.decisions_path.read_bytes(),
            before,
        )


if __name__ == "__main__":
    unittest.main()
