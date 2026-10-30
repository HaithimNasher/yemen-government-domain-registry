import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DataQualityTests(unittest.TestCase):

    def test_audit_passes(self):
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
            result.stdout + result.stderr
        )


if __name__ == "__main__":
    unittest.main()
