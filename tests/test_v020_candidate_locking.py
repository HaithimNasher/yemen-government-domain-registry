import fcntl
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RUNNER = """
import sys
from pathlib import Path
from scripts import collect_source_evidence as c

root = Path(sys.argv[1])
c.ROOT = root
c.REGISTRY = root / "data/governance/evidence_registry.json"
c.validator.load_entity_ids = lambda: {"YE-TEST-001"}

c.collect(
    entity_id="YE-TEST-001",
    source_url="https://example.org/evidence",
    evidence_type="entity_existence",
    discovered_from="Lock test",
    notes="Pending review",
    source_candidate_url="https://example.org/candidate",
)
"""


class CandidateLockingTests(unittest.TestCase):

    def test_collection_waits_for_candidate_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            governance = root / "data/governance"
            governance.mkdir(parents=True)

            registry = governance / "evidence_registry.json"
            registry.write_text("[]\n", encoding="utf-8")

            candidates = {
                "version": "0.19.0",
                "records": [{
                    "entity_id": "YE-TEST-001",
                    "candidate_source_url":
                        "https://example.org/candidate",
                    "review_status": "pending",
                    "ownership_verified": False,
                }],
            }

            (governance / "source_candidates.json").write_text(
                json.dumps(candidates),
                encoding="utf-8",
            )

            lock_path = governance / "source_candidates.json.lock"

            with lock_path.open("a+") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        RUNNER,
                        str(root),
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                try:
                    time.sleep(0.4)

                    self.assertIsNone(
                        process.poll(),
                        "Collector exited while lock was held",
                    )
                finally:
                    fcntl.flock(
                        lock.fileno(),
                        fcntl.LOCK_UN,
                    )

            try:
                stdout, stderr = process.communicate(
                    timeout=10
                )
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                self.fail("Collector did not finish after unlock")

            self.assertEqual(
                process.returncode,
                0,
                stderr,
            )

            records = json.loads(
                registry.read_text(encoding="utf-8")
            )

            self.assertEqual(len(records), 1)
            self.assertEqual(
                records[0]["verification_status"],
                "pending",
            )


if __name__ == "__main__":
    unittest.main()
