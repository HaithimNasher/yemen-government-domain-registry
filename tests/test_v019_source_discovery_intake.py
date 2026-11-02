"""Isolated tests for source discovery intake."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RUNNER = """
import sys
from pathlib import Path
from scripts import add_source_candidate
from scripts import source_discovery_intake

add_source_candidate.ROOT = Path(sys.argv[1])
add_source_candidate.QUEUE = (
    add_source_candidate.ROOT
    / "data/governance/source_candidates.json"
)

sys.argv = [
    "source_discovery_intake.py",
    *sys.argv[2:],
]

source_discovery_intake.main()
"""


class SourceDiscoveryIntakeTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        governance = self.root / "data" / "governance"
        governance.mkdir(parents=True)

        self.candidates = (
            governance / "source_candidates.json"
        )

        self.candidates.write_text(
            json.dumps({
                "version": "0.17.0",
                "records": [],
            }),
            encoding="utf-8",
        )

        (governance / "source_reviews.json").write_text(
            json.dumps([{
                "entity_id": "YE-TEST-001",
                "source_file": "test.json",
                "verification_status": "unverified",
            }]),
            encoding="utf-8",
        )

    def run_intake(self, *args):
        return subprocess.run(
            [
                sys.executable,
                "-c",
                RUNNER,
                str(self.root),
                *args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )

    def valid_args(self):
        return [
            "--entity-id", "YE-TEST-001",
            "--url", "https://example.org/source",
            "--discovered-from", "Manual research",
            "--notes", "Requires independent review",
        ]

    def records(self):
        return json.loads(
            self.candidates.read_text(encoding="utf-8")
        )["records"]

    def test_valid_intake(self):
        result = self.run_intake(*self.valid_args())

        self.assertEqual(
            result.returncode,
            0,
            result.stderr,
        )

        records = self.records()
        self.assertEqual(len(records), 1)

        record = records[0]
        self.assertEqual(
            record["review_status"],
            "pending",
        )
        self.assertIs(
            record["ownership_verified"],
            False,
        )
        self.assertIn(
            "Discovery origin: Manual research",
            record["review_notes"],
        )
        self.assertIn(
            "Discovered at:",
            record["review_notes"],
        )

    def test_invalid_url(self):
        args = self.valid_args()
        args[3] = "https://INVALID-HOST"

        result = self.run_intake(*args)

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "Invalid source URL",
            result.stderr,
        )
        self.assertEqual(self.records(), [])

    def test_empty_discovery_origin(self):
        args = self.valid_args()
        args[5] = "   "

        result = self.run_intake(*args)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.records(), [])

    def test_duplicate_candidate(self):
        first = self.run_intake(*self.valid_args())
        second = self.run_intake(*self.valid_args())

        self.assertEqual(first.returncode, 0)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(len(self.records()), 1)


if __name__ == "__main__":
    unittest.main()
