import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class InstitutionEvidenceTests(unittest.TestCase):

    def test_evidence_records(self):
        path = ROOT / "data/evidence/institutions.json"

        records = json.loads(
            path.read_text(encoding="utf-8")
        )

        self.assertIsInstance(records, list)

        ids = []

        for record in records:
            self.assertTrue(record["entity_id"])
            self.assertIn(
                record["review_status"],
                {"pending", "reviewed", "rejected"}
            )
            self.assertFalse(record["ownership_verified"])
            ids.append(record["entity_id"])

        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
