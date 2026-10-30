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

class DomainOwnershipPolicyTests(unittest.TestCase):

    def ownership_record(self, status):
        return {
            "evidence_id": "EV-OWN-001",
            "entity_id": "YE-UNI-SANAA",
            "evidence_type": "domain_ownership",
            "source_url": "https://su.edu.ye/",
            "verification_status": status,
            "reviewed_at": "2026-10-30",
            "review_notes": "Metadata-only test"
        }

    def test_ownership_cannot_be_self_verified(self):
        errors = validate([
            self.ownership_record("verified")
        ])
        self.assertTrue(
            any("independent verification" in e for e in errors)
        )

    def test_ownership_can_remain_pending(self):
        record = self.ownership_record("pending")
        record.update({
            "domain": "su.edu.ye",
            "verification_method": "document_review",
            "evidence_reference": "PENDING-REVIEW",
            "reviewed_by": "PENDING"
        })
        errors = validate([record])
        self.assertEqual(errors, [])

class DomainOwnershipSchemaTests(unittest.TestCase):

    def base_record(self):
        return {
            "evidence_id": "EV-OWN-SCHEMA-001",
            "entity_id": "YE-UNI-SANAA",
            "evidence_type": "domain_ownership",
            "source_url": "https://su.edu.ye/",
            "verification_status": "pending",
            "reviewed_at": None,
            "review_notes": None,
            "domain": "su.edu.ye",
            "verification_method": "document_review",
            "evidence_reference": "PENDING-REVIEW",
            "reviewed_by": "PENDING"
        }

    def test_complete_ownership_metadata_accepted_as_pending(self):
        self.assertEqual(validate([self.base_record()]), [])

    def test_missing_ownership_fields_rejected(self):
        for field in (
            "domain",
            "verification_method",
            "evidence_reference",
            "reviewed_by",
        ):
            with self.subTest(field=field):
                record = self.base_record()
                record.pop(field)
                errors = validate([record])
                self.assertTrue(
                    any(field in error for error in errors)
                )

    def test_ownership_still_cannot_be_verified(self):
        record = self.base_record()
        record["verification_status"] = "verified"
        record["reviewed_at"] = "2026-10-30"
        record["review_notes"] = "Test metadata only"
        errors = validate([record])
        self.assertTrue(
            any("independent verification" in e for e in errors)
        )

class DomainEntityMatchTests(unittest.TestCase):

    def base_record(self):
        return {
            "evidence_id": "EV-MATCH-001",
            "entity_id": "YE-UNI-SANAA",
            "evidence_type": "domain_ownership",
            "source_url": "https://su.edu.ye/",
            "verification_status": "pending",
            "reviewed_at": None,
            "review_notes": None,
            "domain": "su.edu.ye",
            "verification_method": "document_review",
            "evidence_reference": "PENDING-REVIEW",
            "reviewed_by": "PENDING"
        }

    def test_matching_domain_accepted(self):
        self.assertEqual(validate([self.base_record()]), [])

    def test_mismatching_domain_rejected(self):
        record = self.base_record()
        record["domain"] = "wrong.example"
        errors = validate([record])
        self.assertTrue(
            any("domain does not match entity" in e for e in errors)
        )

    def test_domain_case_normalization(self):
        record = self.base_record()
        record["domain"] = "SU.EDU.YE."
        self.assertEqual(validate([record]), [])
