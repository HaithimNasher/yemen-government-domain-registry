import copy
import unittest
from datetime import date, timedelta

from scripts.validate_source_decisions import validate


class SourceDecisionTests(unittest.TestCase):

    def setUp(self):
        self.candidates = [{
            "entity_id": "YE-TEST-001",
            "candidate_source_url": "https://example.org/source",
            "review_status": "pending",
            "ownership_verified": False,
        }]

        self.reviews = [{
            "entity_id": "YE-TEST-001",
            "source_file": "universities.json",
            "verification_status": "unverified",
        }]

        self.decision = {
            "decision_id": "DEC-TEST-001",
            "entity_id": "YE-TEST-001",
            "candidate_source_url": "https://example.org/source",
            "decision": "accepted",
            "reviewed_by": "Test Reviewer",
            "reviewed_at": date.today().isoformat(),
            "review_notes": "Test evidence reviewed",
            "ownership_verified": False,
        }

    def check_invalid(self, field, value):
        record = copy.deepcopy(self.decision)
        record[field] = value

        errors = validate(
            [record], self.candidates, self.reviews
        )

        self.assertTrue(errors)

    def test_valid_decision(self):
        self.assertEqual(
            validate(
                [self.decision],
                self.candidates,
                self.reviews,
            ),
            [],
        )

    def test_unknown_entity(self):
        self.check_invalid("entity_id", "YE-UNKNOWN")

    def test_unregistered_candidate(self):
        self.check_invalid(
            "candidate_source_url",
            "https://example.org/unknown",
        )

    def test_invalid_url(self):
        self.check_invalid(
            "candidate_source_url",
            "file:///etc/passwd",
        )

    def test_missing_reviewer(self):
        self.check_invalid("reviewed_by", "")

    def test_missing_notes(self):
        self.check_invalid("review_notes", "")

    def test_invalid_decision(self):
        self.check_invalid("decision", "automatically_verified")

    def test_future_date(self):
        future = date.today() + timedelta(days=1)
        self.check_invalid("reviewed_at", future.isoformat())

    def test_ownership_cannot_be_verified(self):
        self.check_invalid("ownership_verified", True)

    def test_duplicate_decision_id(self):
        records = [
            copy.deepcopy(self.decision),
            copy.deepcopy(self.decision),
        ]

        self.assertTrue(
            validate(
                records,
                self.candidates,
                self.reviews,
            )
        )


    def test_conflicting_decisions(self):
        first = copy.deepcopy(self.decision)
        second = copy.deepcopy(self.decision)

        second["decision_id"] = "DEC-TEST-002"
        second["decision"] = "rejected"

        errors = validate(
            [first, second],
            self.candidates,
            self.reviews,
        )

        self.assertTrue(errors)

    def test_empty_registry(self):
        self.assertEqual(
            validate([], self.candidates, self.reviews),
            [],
        )


if __name__ == "__main__":
    unittest.main()
