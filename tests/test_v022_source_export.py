import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import prioritize_source_discovery as module


class SourceExportTests(unittest.TestCase):

    def sample_rows(self):
        return [{
            "priority": 1,
            "priority_reason": "official_source_discovery_needed",
            "entity_id": "YE-MIN-011",
            "name_ar": "وزارة الزراعة",
            "name_en": "Ministry of Agriculture",
            "source_file": "ministries.json",
            "verification_status": "unverified",
            "candidate_count": 0,
            "evidence_count": 0,
            "review_count": 0,
            "discovery_status": "source_discovery_needed",
        }]

    def test_csv_export_preserves_arabic(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "priorities.csv"
            module.export_csv(self.sample_rows(), path)

            with path.open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(
                rows[0]["name_ar"], "وزارة الزراعة"
            )

    def test_csv_header_matches_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "priorities.csv"
            module.export_csv(self.sample_rows(), path)

            with path.open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(
                    reader.fieldnames, module.FIELDS
                )

    def test_empty_export_has_header(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "empty.csv"
            module.export_csv([], path)

            with path.open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(list(reader), [])
                self.assertEqual(
                    reader.fieldnames, module.FIELDS
                )

    def test_build_does_not_mutate_inputs(self):
        reviews = [{
            "entity_id": "YE-MIN-011",
            "source_file": "ministries.json",
            "verification_status": "unverified",
        }]
        candidates = []
        evidence = []
        evidence_reviews = []

        import copy
        original = copy.deepcopy(
            (reviews, candidates, evidence, evidence_reviews)
        )

        module.build_prioritized_queue(
            reviews,
            candidates,
            evidence,
            evidence_reviews,
            enrich=False,
        )

        self.assertEqual(
            (reviews, candidates, evidence, evidence_reviews),
            original,
        )


if __name__ == "__main__":
    unittest.main()
