import unittest

from scripts.sync_source_reviews import build_updated_reviews


class SourceReviewSyncTests(unittest.TestCase):

    def setUp(self):
        self.existing = [{
            "entity_id": "YE-GOV-001",
            "source_file": "governorates.json",
            "verification_status": "unverified",
            "source_url": None,
            "source_type": None,
            "verified_at": None,
            "review_notes": "Source evidence required",
        }]

        self.gaps = [
            {
                "entity_id": "YE-GOV-001",
                "source_file": "governorates.json",
            },
            {
                "entity_id": "YE-UNI-ABYAN",
                "source_file": "universities.json",
            },
        ]

    def test_add_missing_review(self):
        updated, added = build_updated_reviews(
            self.existing, self.gaps
        )

        self.assertEqual(len(updated), 2)
        self.assertEqual(added, ["YE-UNI-ABYAN"])
        self.assertEqual(
            updated[1]["verification_status"],
            "unverified",
        )
        self.assertIsNone(updated[1]["verified_at"])

    def test_original_review_preserved(self):
        updated, _ = build_updated_reviews(
            self.existing, self.gaps
        )

        self.assertEqual(updated[0], self.existing[0])

    def test_idempotency(self):
        updated, _ = build_updated_reviews(
            self.existing, self.gaps
        )

        repeated, added = build_updated_reviews(
            updated, self.gaps
        )

        self.assertEqual(added, [])
        self.assertEqual(repeated, updated)

    def test_reject_duplicate_reviews(self):
        duplicate = self.existing + self.existing

        with self.assertRaises(ValueError):
            build_updated_reviews(duplicate, self.gaps)

    def test_reject_duplicate_gaps(self):
        duplicate = self.gaps + self.gaps

        with self.assertRaises(ValueError):
            build_updated_reviews(self.existing, duplicate)

    def test_reject_missing_entity_id(self):
        invalid = [{
            "entity_id": None,
            "source_file": "universities.json",
        }]

        with self.assertRaises(ValueError):
            build_updated_reviews(self.existing, invalid)


if __name__ == "__main__":
    unittest.main()
