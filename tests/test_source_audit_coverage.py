import unittest

from scripts import audit_sources


class SourceAuditCoverageTests(unittest.TestCase):

    def test_government_bodies_included(self):
        self.assertIn(
            "government_bodies.json",
            audit_sources.FILES,
        )

    def test_public_corporations_included(self):
        self.assertIn(
            "public_corporations.json",
            audit_sources.FILES,
        )

    def test_no_duplicate_files(self):
        self.assertEqual(
            len(audit_sources.FILES),
            len(set(audit_sources.FILES)),
        )

    def test_all_configured_files_exist(self):
        for filename in audit_sources.FILES:
            with self.subTest(filename=filename):
                self.assertTrue(
                    (audit_sources.DATA / filename).is_file(),
                    filename,
                )


if __name__ == "__main__":
    unittest.main()
