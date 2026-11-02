import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_source_discovery_queue import (
    build_queue,
    load_records,
)


class SourceDiscoveryQueueTests(unittest.TestCase):

    def review(self, entity_id, status="unverified"):
        return {
            "entity_id": entity_id,
            "source_file": "ministries.json",
            "verification_status": status,
        }

    def candidate(self, entity_id):
        return {
            "entity_id": entity_id,
            "candidate_source_url":
                "https://example.org/source",
        }

    def test_unverified_entity_is_queued(self):
        result = build_queue(
            [self.review("YE-001")],
            [],
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["discovery_status"],
            "source_discovery_needed",
        )

    def test_verified_entity_is_excluded(self):
        result = build_queue(
            [self.review("YE-001", "verified")],
            [],
        )
        self.assertEqual(result, [])

    def test_candidate_changes_queue_status(self):
        result = build_queue(
            [self.review("YE-001")],
            [self.candidate("YE-001")],
        )
        self.assertEqual(
            result[0]["discovery_status"],
            "candidate_review_needed",
        )
        self.assertEqual(result[0]["candidate_count"], 1)

    def test_multiple_candidates_are_counted(self):
        result = build_queue(
            [self.review("YE-001")],
            [
                self.candidate("YE-001"),
                self.candidate("YE-001"),
            ],
        )
        self.assertEqual(result[0]["candidate_count"], 2)

    def test_duplicate_reviews_are_rejected(self):
        with self.assertRaises(ValueError):
            build_queue(
                [
                    self.review("YE-001"),
                    self.review("YE-001"),
                ],
                [],
            )

    def test_invalid_review_entity_is_rejected(self):
        with self.assertRaises(ValueError):
            build_queue(
                [self.review("")],
                [],
            )

    def test_invalid_candidate_entity_is_rejected(self):
        with self.assertRaises(ValueError):
            build_queue(
                [self.review("YE-001")],
                [self.candidate("")],
            )

    def test_entities_are_sorted(self):
        result = build_queue(
            [
                self.review("YE-003"),
                self.review("YE-001"),
                self.review("YE-002"),
            ],
            [],
        )
        self.assertEqual(
            [row["entity_id"] for row in result],
            ["YE-001", "YE-002", "YE-003"],
        )

    def test_load_records_supports_list(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "records.json"
            path.write_text(
                json.dumps([self.review("YE-001")]),
                encoding="utf-8",
            )
            result = load_records(path)
            self.assertEqual(len(result), 1)

    def test_load_records_supports_object(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "records.json"
            path.write_text(
                json.dumps({
                    "version": "0.19.0",
                    "records": [self.review("YE-001")],
                }),
                encoding="utf-8",
            )
            result = load_records(path)
            self.assertEqual(len(result), 1)

    def test_invalid_records_container_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "records.json"
            path.write_text(
                json.dumps({"records": {}}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_records(path)


if __name__ == "__main__":
    unittest.main()
