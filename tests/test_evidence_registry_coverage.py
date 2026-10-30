import unittest

from scripts import (
    audit_sources,
    audit_domain_verification,
    validate_evidence_registry,
)


class EvidenceRegistryCoverageTests(unittest.TestCase):

    def test_all_source_files_are_covered(self):
        expected = set(audit_sources.FILES)
        actual = set(
            audit_domain_verification.FILES
        )
        self.assertEqual(expected, actual)

    def test_all_registry_entities_are_known(self):
        entity_ids = (
            validate_evidence_registry.load_entity_ids()
        )
        self.assertEqual(len(entity_ids), 524)

    def test_all_entity_domains_are_known(self):
        domains = (
            validate_evidence_registry.load_entity_domains()
        )
        self.assertEqual(len(domains), 521)

    def test_public_corporations_are_known(self):
        ids = validate_evidence_registry.load_entity_ids()
        self.assertTrue(
            any(
                entity_id.startswith("YE-CORP-")
                for entity_id in ids
            )
        )

    def test_unsubstantiated_domain_ownership_rejected(self):
        domains = (
            validate_evidence_registry.load_entity_domains()
        )
        entity_id, domain = next(iter(domains.items()))

        evidence = [{
            "evidence_id": "TEST-OWNERSHIP-001",
            "entity_id": entity_id,
            "evidence_type": "domain_ownership",
            "verification_status": "verified",
            "domain": domain,
            "source_url": "https://example.org",
            "reviewed_at": "2026-01-01",
            "review_notes": "Test only",
            "verification_method": "test",
            "evidence_reference": "test",
            "reviewed_by": "test",
        }]

        errors = validate_evidence_registry.validate(
            evidence
        )

        self.assertTrue(
            any(
                "independent verification workflow" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
