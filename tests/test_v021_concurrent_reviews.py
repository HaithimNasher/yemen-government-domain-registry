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
from scripts import record_evidence_review as r

folder = Path(sys.argv[1])
r.EVIDENCE_PATH = folder / "evidence_registry.json"
r.REVIEWS_PATH = folder / "evidence_reviews.json"
r.validate_evidence = lambda records: []

r.record_review(
    "EV-TEST-001",
    "reviewer-001",
    "accepted_for_review",
    "Concurrent review test",
)
"""


class ConcurrentReviewTests(unittest.TestCase):

    def test_duplicate_concurrent_reviews_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)

            (folder / "evidence_registry.json").write_text(
                json.dumps([{
                    "evidence_id": "EV-TEST-001",
                }]),
                encoding="utf-8",
            )

            reviews_path = folder / "evidence_reviews.json"
            reviews_path.write_text("[]", encoding="utf-8")

            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        RUNNER,
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
                process.communicate(timeout=10)
                for process in processes
            ]

            codes = [
                process.returncode
                for process in processes
            ]

            self.assertEqual(
                sorted(codes), [0, 1],
                str(results),
            )

            records = json.loads(
                reviews_path.read_text(encoding="utf-8")
            )

            self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
