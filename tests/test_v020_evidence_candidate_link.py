import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import collect_source_evidence as collector


class EvidenceCandidateLinkTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        root = Path(self.temp.name)
        governance = root / "data/governance"
        governance.mkdir(parents=True)

        self.registry = governance / "evidence_registry.json"
        self.registry.write_text("[]", encoding="utf-8")

        candidates = {
            "version": "0.17.0",
            "records": [{
                "entity_id": "YE-TEST-001",
                "candidate_source_url": "https://example.org/candidate",
                "review_status": "pending",
                "ownership_verified": False,
            }],
        }

        (governance / "source_candidates.json").write_text(
            json.dumps(candidates),
            encoding="utf-8",
        )

        self.patchers = [
            patch.object(collector, "ROOT", root),
            patch.object(
                collector,
                "REGISTRY",
                self.registry,
            ),
            patch.object(
                collector.validator,
                "load_entity_ids",
                return_value={"YE-TEST-001"},
            ),
        ]

        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def collect(self, candidate_url):
        return collector.collect(
            entity_id="YE-TEST-001",
            source_url="https://example.org/evidence",
            evidence_type="entity_existence",
            discovered_from="Manual research",
            notes="Pending review",
            source_candidate_url=candidate_url,
        )

    def test_valid_candidate_link(self):
        record = self.collect(
            "https://example.org/candidate"
        )

        self.assertEqual(
            record["source_candidate_url"],
            "https://example.org/candidate",
        )
        self.assertEqual(
            record["verification_status"],
            "pending",
        )

    def test_unknown_candidate_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "Pending source candidate not found",
        ):
            self.collect(
                "https://example.org/unknown"
            )

        self.assertEqual(
            json.loads(
                self.registry.read_text(encoding="utf-8")
            ),
            [],
        )


    def test_rejected_candidate_is_not_linked(self):
        candidate_path = (
            self.registry.parent / "source_candidates.json"
        )
        data = json.loads(
            candidate_path.read_text(encoding="utf-8")
        )
        data["records"][0]["review_status"] = "rejected"
        candidate_path.write_text(
            json.dumps(data), encoding="utf-8"
        )

        with self.assertRaisesRegex(
            ValueError, "Pending source candidate not found"
        ):
            self.collect("https://example.org/candidate")

        self.assertEqual(
            json.loads(self.registry.read_text(encoding="utf-8")),
            [],
        )

    def test_verified_ownership_candidate_is_not_linked(self):
        candidate_path = (
            self.registry.parent / "source_candidates.json"
        )
        data = json.loads(
            candidate_path.read_text(encoding="utf-8")
        )
        data["records"][0]["ownership_verified"] = True
        candidate_path.write_text(
            json.dumps(data), encoding="utf-8"
        )

        with self.assertRaisesRegex(
            ValueError, "Pending source candidate not found"
        ):
            self.collect("https://example.org/candidate")

        self.assertEqual(
            json.loads(self.registry.read_text(encoding="utf-8")),
            [],
        )


if __name__ == "__main__":
    unittest.main()
