import unittest

from app.evidence_registry import get_evidence


class EvidenceRegistryTests(unittest.TestCase):

    def test_list_evidence(self):
        result = get_evidence()
        self.assertGreaterEqual(result["total"], 3)

    def test_filter_by_entity(self):
        result = get_evidence("YE-UNI-SANAA")
        self.assertEqual(result["total"], 1)
        self.assertEqual(
            result["results"][0]["entity_id"],
            "YE-UNI-SANAA"
        )

    def test_unknown_entity(self):
        result = get_evidence("YE-UNKNOWN")
        self.assertEqual(result["total"], 0)

    def test_evidence_has_review_status(self):
        result = get_evidence()

        for item in result["results"]:
            self.assertIn(
                item["review_status"],
                {"pending", "reviewed", "rejected"}
            )

    def test_evidence_has_source_fields(self):
        result = get_evidence()

        for item in result["results"]:
            self.assertIn("source_url", item)
            self.assertIn("domain", item)
            self.assertIn("verified_at", item)

    def test_no_verified_ownership(self):
        result = get_evidence()
        for item in result["results"]:
            self.assertFalse(item["ownership_verified"])


if __name__ == "__main__":
    unittest.main()
