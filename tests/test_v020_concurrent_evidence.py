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
from scripts import collect_source_evidence as c

c.REGISTRY = Path(sys.argv[1])
c.validator.load_entity_ids = lambda: {"YE-TEST-001"}

try:
    c.collect(
        entity_id="YE-TEST-001",
        source_url=sys.argv[2],
        evidence_type="entity_existence",
        discovered_from="Concurrency test",
        notes="Isolated test evidence",
    )
except ValueError as exc:
    print(str(exc), file=sys.stderr)
    sys.exit(2)
"""


class ConcurrentEvidenceTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.registry = (
            Path(self.temp.name) / "evidence_registry.json"
        )
        self.registry.write_text(
            "[]\n", encoding="utf-8"
        )

    def launch(self, url):
        return subprocess.Popen(
            [
                sys.executable,
                "-c",
                RUNNER,
                str(self.registry),
                url,
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def records(self):
        return json.loads(
            self.registry.read_text(encoding="utf-8")
        )

    def test_distinct_urls_are_preserved(self):
        first = self.launch("https://example.org/one")
        second = self.launch("https://example.org/two")

        out1, err1 = first.communicate(timeout=15)
        out2, err2 = second.communicate(timeout=15)

        self.assertEqual(first.returncode, 0, err1)
        self.assertEqual(second.returncode, 0, err2)

        records = self.records()
        self.assertEqual(len(records), 2)
        self.assertEqual(
            len({r["evidence_id"] for r in records}),
            2,
        )

    def test_duplicate_url_is_rejected(self):
        first = self.launch("https://example.org/same")
        second = self.launch("https://example.org/same")

        first.communicate(timeout=15)
        second.communicate(timeout=15)

        self.assertEqual(
            sorted([first.returncode, second.returncode]),
            [0, 2],
        )
        self.assertEqual(len(self.records()), 1)


if __name__ == "__main__":
    unittest.main()
