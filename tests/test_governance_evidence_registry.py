import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_evidence_registry import validate

class EvidenceRegistryTests(unittest.TestCase):

    def test_empty_registry(self):
        self.assertEqual(validate([]), [])

    def test_verified_without_source_rejected(self):
        record = {
            "evidence_id": "EV-001",
            "entity_id": "YE-UNI-SANAA",
            "evidence_type": "domain_ownership",
            "source_url": None,
            "verification_status": "verified",
            "reviewed_at": "2026-10-30",
            "review_notes": "Test"
        }
        self.assertTrue(validate([record]))

    def test_duplicate_evidence_rejected(self):
        record = {
            "evidence_id": "EV-001",
            "entity_id": "YE-UNI-SANAA",
            "evidence_type": "domain_observation",
            "source_url": "https://su.edu.ye/",
            "verification_status": "pending",
            "reviewed_at": None,
            "review_notes": None
        }
        self.assertTrue(validate([record, record]))

if __name__ == "__main__":
    unittest.main()

class EvidenceGovernanceStrictTests(unittest.TestCase):

    def valid_record(self):
        return {
            "evidence_id": "EV-TEST-001",
            "entity_id": "YE-UNI-SANAA",
            "evidence_type": "entity_existence",
            "source_url": "https://example.org/evidence",
            "verification_status": "verified",
            "reviewed_at": "2026-10-30",
            "review_notes": "Reviewed against source"
        }

    def test_invalid_review_date_rejected(self):
        record = self.valid_record()
        record["reviewed_at"] = "not-a-date"
        self.assertTrue(validate([record]))

    def test_empty_review_notes_rejected(self):
        record = self.valid_record()
        record["review_notes"] = "   "
        self.assertTrue(validate([record]))

    def test_invalid_verified_url_rejected(self):
        record = self.valid_record()
        record["source_url"] = "invalid-url"
        self.assertTrue(validate([record]))

class EvidenceEntityReferenceTests(unittest.TestCase):

    def test_unknown_entity_rejected(self):
        record = {
            "evidence_id": "EV-UNKNOWN-001",
            "entity_id": "YE-UNKNOWN-999999",
            "evidence_type": "entity_existence",
            "source_url": None,
            "verification_status": "pending",
            "reviewed_at": None,
            "review_notes": None
        }
        errors = validate([record])
        self.assertTrue(
            any("unknown entity_id" in error for error in errors)
        )

    def test_known_entity_accepted(self):
        record = {
            "evidence_id": "EV-KNOWN-001",
            "entity_id": "YE-UNI-SANAA",
            "evidence_type": "entity_existence",
            "source_url": None,
            "verification_status": "pending",
            "reviewed_at": None,
            "review_notes": None
        }
        self.assertEqual(validate([record]), [])
