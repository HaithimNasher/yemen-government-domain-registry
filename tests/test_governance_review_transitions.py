import unittest

from scripts.validate_review_transitions import validate_transitions


class ReviewTransitionTests(unittest.TestCase):

    def review(self, review_id, decision, reviewed_at):
        return {
            "review_id": review_id,
            "evidence_id": "EV-001",
            "reviewer_id": "reviewer-001",
            "decision": decision,
            "reviewed_at": reviewed_at,
            "review_notes": "Transition test",
        }

    def test_information_to_review_accepted(self):
        reviews = [
            self.review("REV-001", "needs_more_information", "2026-10-28"),
            self.review("REV-002", "accepted_for_review", "2026-10-29"),
        ]
        self.assertEqual(validate_transitions(reviews, {"EV-001"}), [])

    def test_review_to_rejection_accepted(self):
        reviews = [
            self.review("REV-001", "accepted_for_review", "2026-10-28"),
            self.review("REV-002", "rejected", "2026-10-29"),
        ]
        self.assertEqual(validate_transitions(reviews, {"EV-001"}), [])

    def test_rejection_cannot_be_reopened(self):
        reviews = [
            self.review("REV-001", "rejected", "2026-10-28"),
            self.review("REV-002", "accepted_for_review", "2026-10-29"),
        ]
        errors = validate_transitions(reviews, {"EV-001"})
        self.assertTrue(
            any("invalid transition" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()


class SameDayReviewTests(unittest.TestCase):

    def review(self, review_id, decision, reviewed_at):
        return {
            "review_id": review_id,
            "evidence_id": "EV-001",
            "reviewer_id": "reviewer-001",
            "decision": decision,
            "reviewed_at": reviewed_at,
            "review_notes": "Same-day review test",
        }

    def test_same_day_conflict_rejected(self):
        reviews = [
            self.review("REV-001", "accepted_for_review", "2026-10-29"),
            self.review("REV-002", "rejected", "2026-10-29"),
        ]
        errors = validate_transitions(reviews, {"EV-001"})
        self.assertTrue(
            any("ambiguous same-day" in e for e in errors)
        )

    def test_same_day_same_decision_allowed(self):
        reviews = [
            self.review("REV-001", "accepted_for_review", "2026-10-29"),
            self.review("REV-002", "accepted_for_review", "2026-10-29"),
        ]
        self.assertEqual(validate_transitions(reviews, {"EV-001"}), [])

    def test_next_day_transition_allowed(self):
        reviews = [
            self.review("REV-001", "accepted_for_review", "2026-10-28"),
            self.review("REV-002", "rejected", "2026-10-29"),
        ]
        self.assertEqual(validate_transitions(reviews, {"EV-001"}), [])

    def test_reverse_same_day_conflict_rejected(self):
        reviews = [
            self.review("REV-001", "rejected", "2026-10-29"),
            self.review("REV-002", "accepted_for_review", "2026-10-29"),
        ]
        errors = validate_transitions(reviews, {"EV-001"})
        self.assertTrue(
            any("ambiguous same-day" in e for e in errors)
        )
