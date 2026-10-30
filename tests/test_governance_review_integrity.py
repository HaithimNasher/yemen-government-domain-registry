import unittest
from datetime import date

from scripts.audit_review_integrity import audit


class ReviewIntegrityTests(unittest.TestCase):

    def review(self, review_id, decision):
        return {
            "review_id": review_id,
            "evidence_id": "EV-001",
            "reviewer_id": "reviewer-001",
            "decision": decision,
            "reviewed_at": date.today().isoformat(),
            "review_notes": "Test review decision",
        }

    def test_single_review_accepted(self):
        errors = audit(
            [self.review("REV-001", "accepted_for_review")],
            {"EV-001"},
        )
        self.assertEqual(errors, [])

    def test_conflicting_decisions_rejected(self):
        reviews = [
            self.review("REV-001", "accepted_for_review"),
            self.review("REV-002", "rejected"),
        ]
        errors = audit(reviews, {"EV-001"})
        self.assertEqual(errors, [])

    def test_same_decision_multiple_reviews_allowed(self):
        reviews = [
            self.review("REV-001", "accepted_for_review"),
            self.review("REV-002", "accepted_for_review"),
        ]
        self.assertEqual(audit(reviews, {"EV-001"}), [])


if __name__ == "__main__":
    unittest.main()

class UnifiedReviewIntegrityTests(unittest.TestCase):

    def review(self, review_id, decision, reviewed_at):
        return {
            "review_id": review_id,
            "evidence_id": "EV-001",
            "reviewer_id": "reviewer-001",
            "decision": decision,
            "reviewed_at": reviewed_at,
            "review_notes": "Review integrity test",
        }

    def test_valid_transition_is_accepted(self):
        reviews = [
            self.review("REV-001", "accepted_for_review", "2026-10-28"),
            self.review("REV-002", "rejected", "2026-10-29"),
        ]
        self.assertEqual(audit(reviews, {"EV-001"}), [])

    def test_reopening_rejected_evidence_is_blocked(self):
        reviews = [
            self.review("REV-001", "rejected", "2026-10-28"),
            self.review("REV-002", "accepted_for_review", "2026-10-29"),
        ]
        errors = audit(reviews, {"EV-001"})
        self.assertTrue(
            any("invalid transition" in e for e in errors)
        )
