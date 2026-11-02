"""Test concurrent candidate registration using isolated files."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ConcurrentCandidateTests(unittest.TestCase):

    def test_concurrent_distinct_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)

            candidates = folder / "source_candidates.json"
            reviews = folder / "source_reviews.json"

            candidates.write_text(
                json.dumps({
                    "version": "0.17.0",
                    "records": [],
                }),
                encoding="utf-8",
            )

            reviews.write_text(
                json.dumps([{
                    "entity_id": "YE-TEST-001",
                    "source_file": "test.json",
                    "verification_status": "unverified",
                }]),
                encoding="utf-8",
            )

            runner = """
import sys
from pathlib import Path
from scripts import add_source_candidate as module

module.QUEUE = Path(sys.argv[1])
module.ROOT = Path(sys.argv[2])
sys.argv = [
    "add_source_candidate.py",
    "--entity-id", "YE-TEST-001",
    "--url", sys.argv[3],
    "--notes", "Concurrency test",
]
module.locked_main()
"""

            governance = folder / "data" / "governance"
            governance.mkdir(parents=True)

            isolated_candidates = (
                governance / "source_candidates.json"
            )
            isolated_reviews = (
                governance / "source_reviews.json"
            )

            isolated_candidates.write_bytes(
                candidates.read_bytes()
            )
            isolated_reviews.write_bytes(
                reviews.read_bytes()
            )

            urls = [
                "https://example.org/one",
                "https://example.org/two",
            ]

            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        runner,
                        str(isolated_candidates),
                        str(folder),
                        url,
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for url in urls
            ]

            for process in processes:
                stdout, stderr = process.communicate(
                    timeout=15
                )
                self.assertEqual(
                    process.returncode,
                    0,
                    msg=stdout + stderr,
                )

            result = json.loads(
                isolated_candidates.read_text(
                    encoding="utf-8"
                )
            )

            records = result["records"]

            self.assertEqual(len(records), 2)

            self.assertEqual(
                {
                    item["candidate_source_url"]
                    for item in records
                },
                set(urls),
            )

            self.assertTrue(
                all(
                    item["ownership_verified"] is False
                    for item in records
                )
            )

            self.assertTrue(
                all(
                    item["review_status"] == "pending"
                    for item in records
                )
            )


    def test_concurrent_duplicate_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            governance = folder / "data" / "governance"
            governance.mkdir(parents=True)

            candidates = governance / "source_candidates.json"
            reviews = governance / "source_reviews.json"

            candidates.write_text(
                json.dumps({
                    "version": "0.17.0",
                    "records": [],
                }),
                encoding="utf-8",
            )

            reviews.write_text(
                json.dumps([{
                    "entity_id": "YE-TEST-001",
                    "source_file": "test.json",
                    "verification_status": "unverified",
                }]),
                encoding="utf-8",
            )

            runner = """
import sys
from pathlib import Path
from scripts import add_source_candidate as module

module.QUEUE = Path(sys.argv[1])
module.ROOT = Path(sys.argv[2])
sys.argv = [
    "add_source_candidate.py",
    "--entity-id", "YE-TEST-001",
    "--url", "https://example.org/same",
    "--notes", "Duplicate concurrency test",
]
module.locked_main()
"""

            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        runner,
                        str(candidates),
                        str(folder),
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for _ in range(2)
            ]

            results = [
                process.communicate(timeout=15)
                for process in processes
            ]

            codes = [
                process.returncode
                for process in processes
            ]

            self.assertEqual(sorted(codes), [0, 1])

            records = json.loads(
                candidates.read_text(encoding="utf-8")
            )["records"]

            self.assertEqual(len(records), 1)
            self.assertEqual(
                records[0]["candidate_source_url"],
                "https://example.org/same",
            )
            self.assertIs(
                records[0]["ownership_verified"],
                False,
            )


if __name__ == "__main__":
    unittest.main()
