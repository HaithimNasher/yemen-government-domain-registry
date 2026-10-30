import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DomainDNSTests(unittest.TestCase):

    def test_dns_report_generation(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_domain_dns.py")
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

        report = json.loads(
            (ROOT / "domain-dns-report.json")
            .read_text(encoding="utf-8")
        )

        self.assertFalse(report["live_checks"])

        for item in report["results"]:
            self.assertFalse(
                item["ownership_verified"]
            )
            self.assertEqual(
                item["dns_status"],
                "not_checked"
            )


if __name__ == "__main__":
    unittest.main()
