import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import collect_source_evidence as collector


class SourceEvidenceCollectionTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.registry = (
            Path(self.temp.name)
            / "evidence_registry.json"
        )
        self.registry.write_text(
            "[]\n",
            encoding="utf-8",
        )

        self.path_patch = patch.object(
            collector,
            "REGISTRY",
            self.registry,
        )
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

        self.ids_patch = patch.object(
            collector.validator,
            "load_entity_ids",
            return_value={"YE-TEST-001"},
        )
        self.ids_patch.start()
        self.addCleanup(self.ids_patch.stop)

    def add(self, **overrides):
        args = {
            "entity_id": "YE-TEST-001",
            "source_url": "https://example.org/evidence",
            "evidence_type": "entity_existence",
            "discovered_from": "Manual research",
            "notes": "Awaiting independent review",
        }
        args.update(overrides)
        return collector.collect(**args)

    def records(self):
        return json.loads(
            self.registry.read_text(encoding="utf-8")
        )

    def test_valid_evidence_is_pending(self):
        record = self.add()

        self.assertEqual(
            record["verification_status"],
            "pending",
        )
        self.assertIsNone(record["reviewed_at"])
        self.assertEqual(len(self.records()), 1)

    def test_duplicate_is_rejected(self):
        self.add()

        with self.assertRaisesRegex(
            ValueError, "Duplicate evidence"
        ):
            self.add()

        self.assertEqual(len(self.records()), 1)

    def test_unknown_entity_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "Unknown entity"
        ):
            self.add(entity_id="YE-UNKNOWN")

        self.assertEqual(self.records(), [])

    def test_invalid_url_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add(source_url="https://INVALID-HOST")

        self.assertEqual(self.records(), [])

    def test_ownership_intake_is_blocked(self):
        with self.assertRaisesRegex(
            ValueError, "Unsupported intake"
        ):
            self.add(evidence_type="domain_ownership")

        self.assertEqual(self.records(), [])

    def test_missing_metadata_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add(discovered_from="   ")

        self.assertEqual(self.records(), [])

    def test_different_evidence_types_allowed(self):
        self.add()
        self.add(evidence_type="official_website")

        self.assertEqual(len(self.records()), 2)


if __name__ == "__main__":
    unittest.main()
