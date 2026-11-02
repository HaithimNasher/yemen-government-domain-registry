import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import export_source_discovery as exporter
from scripts import enrich_source_discovery_queue as enricher


class SourceDiscoveryExportTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        governance = self.data / "governance"
        governance.mkdir(parents=True)

        self.reviews = governance / "source_reviews.json"
        self.candidates = governance / "source_candidates.json"

        self.reviews.write_text(
            json.dumps([{
                "entity_id": "YE-TEST-001",
                "source_file": "institutions.json",
                "verification_status": "unverified",
            }]),
            encoding="utf-8",
        )

        self.candidates.write_text(
            json.dumps({
                "version": "0.17.0",
                "records": [],
            }),
            encoding="utf-8",
        )

        (self.data / "institutions.json").write_text(
            json.dumps([{
                "entity_id": "YE-TEST-001",
                "name_ar": "مؤسسة تجريبية",
                "name_en": "Test Institution",
            }], ensure_ascii=False),
            encoding="utf-8",
        )

        self.root_patch = patch.object(
            exporter, "ROOT", self.root
        )
        self.data_patch = patch.object(
            enricher, "DATA", self.data
        )

        self.root_patch.start()
        self.data_patch.start()

        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.data_patch.stop)

    def test_export_csv_content(self):
        output = self.root / "report.csv"

        count = exporter.export_queue(output)

        with output.open(
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(count, 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["name_ar"],
            "مؤسسة تجريبية",
        )
        self.assertEqual(
            rows[0]["discovery_status"],
            "source_discovery_needed",
        )

    def test_export_columns(self):
        output = self.root / "report.csv"
        exporter.export_queue(output)

        with output.open(
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(
                reader.fieldnames,
                exporter.FIELDS,
            )

    def test_export_does_not_modify_registries(self):
        before_reviews = self.reviews.read_bytes()
        before_candidates = self.candidates.read_bytes()

        exporter.export_queue(
            self.root / "report.csv"
        )

        self.assertEqual(
            self.reviews.read_bytes(),
            before_reviews,
        )
        self.assertEqual(
            self.candidates.read_bytes(),
            before_candidates,
        )


if __name__ == "__main__":
    unittest.main()
