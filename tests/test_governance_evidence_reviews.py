import unittest
from datetime import date, timedelta

from scripts.validate_evidence_reviews import validate


class EvidenceReviewTests(unittest.TestCase):

    def base_review(self):
        return {
            "review_id": "REV-001",
            "evidence_id": "EV-001",
            "reviewer_id": "reviewer-001",
            "decision": "accepted_for_review",
            "reviewed_at": date.today().isoformat(),
            "review_notes": "Evidence accepted for further review",
        }

    def test_valid_review(self):
        self.assertEqual(
            validate([self.base_review()], {"EV-001"}),
            [],
        )

    def test_unknown_evidence_rejected(self):
        errors = validate([self.base_review()], set())
        self.assertTrue(
            any("unknown evidence_id" in e for e in errors)
        )

    def test_duplicate_review_id_rejected(self):
        record = self.base_review()
        errors = validate([record, record.copy()], {"EV-001"})
        self.assertTrue(
            any("duplicate review_id" in e for e in errors)
        )

    def test_invalid_decision_rejected(self):
        record = self.base_review()
        record["decision"] = "ownership_verified"
        errors = validate([record], {"EV-001"})
        self.assertTrue(
            any("invalid decision" in e for e in errors)
        )

    def test_future_date_rejected(self):
        record = self.base_review()
        record["reviewed_at"] = (
            date.today() + timedelta(days=1)
        ).isoformat()
        errors = validate([record], {"EV-001"})
        self.assertTrue(
            any("future review date" in e for e in errors)
        )

    def test_missing_reviewer_rejected(self):
        record = self.base_review()
        record["reviewer_id"] = ""
        errors = validate([record], {"EV-001"})
        self.assertTrue(
            any("missing reviewer_id" in e for e in errors)
        )


if __name__ == "__main__":
    unittest.main()
