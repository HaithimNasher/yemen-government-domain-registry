import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SourceReviewTests(unittest.TestCase):

    def test_review_records_are_unique(self):
        path = ROOT / "data/governance/source_reviews.json"

        records = json.loads(
            path.read_text(encoding="utf-8")
        )

        ids = [r["entity_id"] for r in records]

        self.assertEqual(len(ids), len(set(ids)))

    def test_review_statuses_are_valid(self):
        path = ROOT / "data/governance/source_reviews.json"

        records = json.loads(
            path.read_text(encoding="utf-8")
        )

        allowed = {
            "unverified",
            "under_review",
            "verified",
            "rejected"
        }

        for record in records:
            self.assertIn(
                record["verification_status"],
                allowed
            )

            if record["verification_status"] == "verified":
                self.assertTrue(record["source_url"])
                self.assertTrue(record["verified_at"])


if __name__ == "__main__":
    unittest.main()
