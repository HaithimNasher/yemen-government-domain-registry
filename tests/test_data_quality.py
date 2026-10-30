import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DataQualityTests(unittest.TestCase):

    def test_data_quality_audit(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "audit_data_quality.py")
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )

        report_path = ROOT / "data-quality-report.json"

        self.assertTrue(report_path.exists())

        report = json.loads(
            report_path.read_text(encoding="utf-8")
        )

        self.assertEqual(report["errors"], 0)
        self.assertGreater(report["total_records"], 0)


if __name__ == "__main__":
    unittest.main()
