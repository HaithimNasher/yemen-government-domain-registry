import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import audit_sources


class SourceAuditTests(unittest.TestCase):

    def test_audit_produces_report(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "audit.json"

            with patch.object(audit_sources, "OUTPUT", output):
                result = audit_sources.audit()

            self.assertEqual(result, 0)
            self.assertTrue(output.exists())

            report = json.loads(
                output.read_text(encoding="utf-8")
            )

            self.assertEqual(report["version"], "0.7.0")
            self.assertGreater(report["total_records"], 0)
            self.assertEqual(report["invalid_sources"], 0)

    def test_missing_source_is_reported(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data"
            data.mkdir()

            (data / "ministries.json").write_text(
                json.dumps([
                    {
                        "entity_id": "YE-TEST-001",
                        "source_url": None
                    }
                ]),
                encoding="utf-8"
            )

            with patch.object(audit_sources, "DATA", data), \
                 patch.object(
                     audit_sources,
                     "OUTPUT",
                     root / "audit.json"
                 ), \
                 patch.object(
                     audit_sources,
                     "FILES",
                     ["ministries.json"]
                 ):
                result = audit_sources.audit()

            self.assertEqual(result, 0)

            report = json.loads(
                (root / "audit.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(report["missing_sources"], 1)


if __name__ == "__main__":
    unittest.main()
