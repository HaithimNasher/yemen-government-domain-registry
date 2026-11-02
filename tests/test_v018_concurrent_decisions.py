import json
import multiprocessing
import tempfile
import unittest
from pathlib import Path

from scripts.record_source_decision import locked_record_decision


def worker(queue, paths):
    try:
        locked_record_decision(
            entity_id="YE-TEST-001",
            url="https://example.org/source",
            decision="accepted",
            reviewer="Test Reviewer",
            notes="Concurrency test",
            decisions_path=Path(paths[0]),
            candidates_path=Path(paths[1]),
            reviews_path=Path(paths[2]),
        )
        queue.put("success")
    except ValueError:
        queue.put("rejected")
    except Exception as exc:
        queue.put("error:" + repr(exc))


class ConcurrentDecisionTests(unittest.TestCase):

    def test_concurrent_duplicate_decisions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            decisions = root / "decisions.json"
            candidates = root / "candidates.json"
            reviews = root / "reviews.json"

            decisions.write_text(json.dumps({
                "version": "0.18.0",
                "records": [],
            }), encoding="utf-8")

            candidates.write_text(json.dumps({
                "version": "0.17.0",
                "records": [{
                    "entity_id": "YE-TEST-001",
                    "candidate_source_url":
                        "https://example.org/source",
                    "review_status": "pending",
                    "ownership_verified": False,
                }],
            }), encoding="utf-8")

            reviews.write_text(json.dumps([{
                "entity_id": "YE-TEST-001",
                "verification_status": "unverified",
            }]), encoding="utf-8")

            paths = (
                str(decisions),
                str(candidates),
                str(reviews),
            )

            queue = multiprocessing.Queue()

            processes = [
                multiprocessing.Process(
                    target=worker,
                    args=(queue, paths),
                )
                for _ in range(2)
            ]

            for process in processes:
                process.start()

            for process in processes:
                process.join(timeout=10)
                if process.is_alive():
                    process.terminate()
                    process.join()
                    self.fail("Worker timed out")

                self.assertEqual(process.exitcode, 0)

            results = [queue.get(timeout=5) for _ in processes]

            self.assertEqual(results.count("success"), 1)
            self.assertEqual(results.count("rejected"), 1)

            stored = json.loads(
                decisions.read_text(encoding="utf-8")
            )["records"]

            self.assertEqual(len(stored), 1)
            self.assertFalse(stored[0]["ownership_verified"])


if __name__ == "__main__":
    unittest.main()
