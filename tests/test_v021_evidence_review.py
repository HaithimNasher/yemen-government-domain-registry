import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import record_evidence_review as module


class EvidenceReviewWorkflowTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        root = Path(self.temp.name)
        self.evidence = root / "evidence_registry.json"
        self.reviews = root / "evidence_reviews.json"

        self.evidence.write_text(
            json.dumps([{
                "evidence_id": "EV-TEST-001",
                "entity_id": "YE-TEST-001",
                "evidence_type": "entity_existence",
                "source_url": "https://example.org/source",
                "verification_status": "pending",
                "reviewed_at": None,
                "review_notes": None,
            }]),
            encoding="utf-8",
        )
        self.reviews.write_text("[]", encoding="utf-8")

        patchers = [
            patch.object(module, "EVIDENCE_PATH", self.evidence),
            patch.object(module, "REVIEWS_PATH", self.reviews),
            patch.object(
                module,
                "validate_evidence",
                return_value=[],
            ),
        ]

        for item in patchers:
            item.start()
            self.addCleanup(item.stop)

    def submit(self, decision="accepted_for_review", **kwargs):
        args = {
            "evidence_id": "EV-TEST-001",
            "reviewer_id": "reviewer-001",
            "decision": decision,
            "notes": "Manual governance review",
        }
        args.update(kwargs)
        return module.record_review(**args)

    def records(self):
        return json.loads(
            self.reviews.read_text(encoding="utf-8")
        )

    def test_review_is_recorded(self):
        result = self.submit()
        self.assertEqual(
            result["decision"], "accepted_for_review"
        )
        self.assertEqual(len(self.records()), 1)

    def test_unknown_evidence_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "Unknown evidence_id"
        ):
            self.submit(evidence_id="EV-UNKNOWN")

        self.assertEqual(self.records(), [])

    def test_duplicate_decision_rejected(self):
        self.submit()

        with self.assertRaisesRegex(
            ValueError, "Duplicate reviewer decision"
        ):
            self.submit()

        self.assertEqual(len(self.records()), 1)

    def test_conflicting_same_day_decision_rejected(self):
        self.submit()

        with self.assertRaisesRegex(
            ValueError, "ambiguous same-day"
        ):
            self.submit(decision="rejected")

        self.assertEqual(len(self.records()), 1)

    def test_invalid_decision_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "Invalid review decision"
        ):
            self.submit(decision="ownership_verified")

        self.assertEqual(self.records(), [])

    def test_evidence_is_not_modified(self):
        before = self.evidence.read_bytes()
        self.submit()
        self.assertEqual(
            self.evidence.read_bytes(), before
        )

    def test_missing_reviewer_rejected(self):
        with self.assertRaises(ValueError):
            self.submit(reviewer_id=" ")

        self.assertEqual(self.records(), [])


    def test_rejected_evidence_cannot_reopen(self):
        self.submit(decision="rejected")

        from datetime import date, timedelta
        from unittest.mock import patch

        # Simulate a subsequent day without changing
        # the actual system clock.
        next_day = date.today() + timedelta(days=1)

        class FakeDate:
            @staticmethod
            def today():
                return next_day

        with patch.object(module, "date", FakeDate):
            with self.assertRaisesRegex(
                ValueError, "invalid transition"
            ):
                self.submit(
                    decision="accepted_for_review"
                )

        self.assertEqual(len(self.records()), 1)

    def test_missing_notes_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "Missing required"
        ):
            self.submit(notes=" ")

        self.assertEqual(self.records(), [])

    def test_different_reviewers_same_decision(self):
        self.submit(reviewer_id="reviewer-001")
        self.submit(reviewer_id="reviewer-002")

        self.assertEqual(len(self.records()), 2)


if __name__ == "__main__":
    unittest.main()
