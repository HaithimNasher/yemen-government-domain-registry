import unittest

from scripts.prioritize_source_discovery import (
    build_prioritized_queue,
)


class SourcePriorityTests(unittest.TestCase):

    def review(self, entity_id, source_file):
        return {
            "entity_id": entity_id,
            "source_file": source_file,
            "verification_status": "unverified",
        }

    def candidate(self, entity_id):
        return {
            "entity_id": entity_id,
            "candidate_source_url":
                "https://example.org/source",
            "review_status": "pending",
        }

    def build(
        self,
        reviews,
        candidates=None,
        evidence=None,
        evidence_reviews=None,
    ):
        return build_prioritized_queue(
            reviews,
            candidates or [],
            evidence or [],
            evidence_reviews or [],
            enrich=False,
        )

    def test_ministry_before_university(self):
        rows = self.build([
            self.review("YE-UNI-001", "universities.json"),
            self.review("YE-MIN-001", "ministries.json"),
        ])
        self.assertEqual(
            [x["entity_id"] for x in rows],
            ["YE-MIN-001", "YE-UNI-001"],
        )

    def test_without_candidates_first(self):
        rows = self.build(
            [
                self.review("YE-MIN-001", "ministries.json"),
                self.review("YE-GOV-001", "governorates.json"),
            ],
            [self.candidate("YE-MIN-001")],
        )
        self.assertEqual(
            rows[0]["entity_id"], "YE-GOV-001"
        )

    def test_evidence_count(self):
        rows = self.build(
            [self.review("YE-MIN-001", "ministries.json")],
            evidence=[{
                "evidence_id": "EV-001",
                "entity_id": "YE-MIN-001",
            }],
        )
        self.assertEqual(rows[0]["evidence_count"], 1)

    def test_review_count(self):
        rows = self.build(
            [self.review("YE-MIN-001", "ministries.json")],
            evidence=[{
                "evidence_id": "EV-001",
                "entity_id": "YE-MIN-001",
            }],
            evidence_reviews=[{
                "evidence_id": "EV-001",
            }],
        )
        self.assertEqual(rows[0]["review_count"], 1)

    def test_unknown_evidence_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "Unknown reviewed evidence"
        ):
            self.build(
                [self.review("YE-MIN-001", "ministries.json")],
                evidence_reviews=[{
                    "evidence_id": "EV-UNKNOWN",
                }],
            )

    def test_deterministic_order(self):
        reviews = [
            self.review("YE-MIN-002", "ministries.json"),
            self.review("YE-MIN-001", "ministries.json"),
        ]

        first = self.build(reviews)
        second = self.build(list(reversed(reviews)))

        self.assertEqual(first, second)

    def test_duplicate_evidence_rejected(self):
        evidence = [
            {
                "evidence_id": "EV-001",
                "entity_id": "YE-MIN-001",
            },
            {
                "evidence_id": "EV-001",
                "entity_id": "YE-MIN-001",
            },
        ]

        with self.assertRaisesRegex(
            ValueError, "Duplicate evidence_id"
        ):
            self.build(
                [self.review("YE-MIN-001", "ministries.json")],
                evidence=evidence,
            )


if __name__ == "__main__":
    unittest.main()
