import unittest

from scripts import (
    audit_domain_verification,
    audit_sources,
)


class DomainAuditCoverageTests(unittest.TestCase):

    def test_all_source_files_are_audited(self):
        self.assertEqual(
            set(audit_domain_verification.FILES),
            set(audit_sources.FILES),
        )

    def test_public_corporations_included(self):
        self.assertIn(
            "public_corporations.json",
            audit_domain_verification.FILES,
        )

    def test_government_bodies_included(self):
        self.assertIn(
            "government_bodies.json",
            audit_domain_verification.FILES,
        )

    def test_no_duplicate_files(self):
        files = audit_domain_verification.FILES
        self.assertEqual(len(files), len(set(files)))

    def test_all_configured_files_exist(self):
        for filename in audit_domain_verification.FILES:
            with self.subTest(filename=filename):
                self.assertTrue(
                    (audit_domain_verification.DATA / filename).is_file(),
                    filename,
                )


if __name__ == "__main__":
    unittest.main()
