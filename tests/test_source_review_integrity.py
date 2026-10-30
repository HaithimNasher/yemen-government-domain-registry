import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

FILES = [
    "governorates.json",
    "districts.json",
    "ministries.json",
    "universities.json",
    "government_services.json",
]


class SourceReviewIntegrityTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.entities = {}

        for filename in FILES:
            records = json.loads(
                (DATA / filename).read_text(encoding="utf-8")
            )

            for record in records:
                cls.entities[record["entity_id"]] = record

        cls.reviews = json.loads(
            (DATA / "governance/source_reviews.json").read_text(
                encoding="utf-8"
            )
        )

    def test_review_entities_exist(self):
        for review in self.reviews:
            self.assertIn(
                review["entity_id"],
                self.entities
            )

    def test_verified_requires_evidence(self):
        for review in self.reviews:
            if review["verification_status"] != "verified":
                continue

            source = review.get("source_url")
            verified_at = review.get("verified_at")
            source_type = review.get("source_type")

            self.assertIsInstance(source, str)
            self.assertTrue(source)
            self.assertTrue(verified_at)
            self.assertTrue(source_type)

            parsed = urlparse(source)
            self.assertIn(parsed.scheme, ("https", "http"))
            self.assertTrue(parsed.netloc)

    def test_unverified_has_no_verification_date(self):
        for review in self.reviews:
            if review["verification_status"] == "unverified":
                self.assertIsNone(review.get("verified_at"))


if __name__ == "__main__":
    unittest.main()
