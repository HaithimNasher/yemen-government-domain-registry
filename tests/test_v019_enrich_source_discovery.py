import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.enrich_source_discovery_queue import (
    load_entity_names,
    enrich_queue,
)


class EnrichSourceDiscoveryTests(unittest.TestCase):

    def test_load_entity_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "entities.json"

            path.write_text(json.dumps([{
                "entity_id": "YE-001",
                "name_ar": "مؤسسة تجريبية",
                "name_en": "Test Institution",
            }]), encoding="utf-8")

            with patch(
                "scripts.enrich_source_discovery_queue.DATA",
                root,
            ):
                names = load_entity_names("entities.json")

            self.assertEqual(
                names["YE-001"]["name_ar"],
                "مؤسسة تجريبية",
            )

    def test_duplicate_entity_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "entities.json").write_text(
                json.dumps([
                    {"entity_id": "YE-001"},
                    {"entity_id": "YE-001"},
                ]),
                encoding="utf-8",
            )

            with patch(
                "scripts.enrich_source_discovery_queue.DATA",
                root,
            ):
                with self.assertRaises(ValueError):
                    load_entity_names("entities.json")

    def test_missing_source_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch(
                "scripts.enrich_source_discovery_queue.DATA",
                Path(temp),
            ):
                with self.assertRaises(ValueError):
                    load_entity_names("missing.json")

    def test_missing_entity_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "entities.json").write_text(
                "[]",
                encoding="utf-8",
            )

            queue = [{
                "entity_id": "YE-001",
                "source_file": "entities.json",
            }]

            with patch(
                "scripts.enrich_source_discovery_queue.DATA",
                root,
            ):
                with self.assertRaises(ValueError):
                    enrich_queue(queue)

    def test_enrichment_preserves_original_queue(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "entities.json").write_text(
                json.dumps([{
                    "entity_id": "YE-001",
                    "name_ar": "مؤسسة تجريبية",
                    "name_en": "Test Institution",
                }]),
                encoding="utf-8",
            )

            queue = [{
                "entity_id": "YE-001",
                "source_file": "entities.json",
                "candidate_count": 0,
            }]

            original = json.loads(json.dumps(queue))

            with patch(
                "scripts.enrich_source_discovery_queue.DATA",
                root,
            ):
                result = enrich_queue(queue)

            self.assertEqual(queue, original)
            self.assertEqual(
                result[0]["name_en"],
                "Test Institution",
            )
            self.assertEqual(
                result[0]["candidate_count"],
                0,
            )


if __name__ == "__main__":
    unittest.main()
