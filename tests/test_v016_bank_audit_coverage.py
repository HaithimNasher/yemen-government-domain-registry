import json
import unittest
from pathlib import Path

from scripts import (
    audit_sources,
    audit_domain_verification,
    validate_evidence_registry,
)

ROOT = Path(__file__).resolve().parents[1]
BANKS = ROOT / "data/banks_candidates.json"


class BankAuditCoverageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.banks = json.loads(
            BANKS.read_text(encoding="utf-8")
        )

    def test_bank_file_in_source_audit(self):
        self.assertIn(
            "banks_candidates.json",
            audit_sources.FILES,
        )

    def test_bank_file_in_domain_audit(self):
        self.assertIn(
            "banks_candidates.json",
            audit_domain_verification.FILES,
        )

    def test_audit_file_lists_match(self):
        self.assertEqual(
            set(audit_sources.FILES),
            set(audit_domain_verification.FILES),
        )

    def test_all_bank_ids_known_to_evidence(self):
        known = validate_evidence_registry.load_entity_ids()

        for bank in self.banks:
            with self.subTest(bank=bank["entity_id"]):
                self.assertIn(bank["entity_id"], known)

    def test_all_bank_domains_known_to_evidence(self):
        known = (
            validate_evidence_registry.load_entity_domains()
        )

        for bank in self.banks:
            if bank.get("domain"):
                with self.subTest(bank=bank["entity_id"]):
                    self.assertEqual(
                        known.get(bank["entity_id"]),
                        bank["domain"].lower().rstrip("."),
                    )

    def test_no_bank_claims_verified_ownership(self):
        for bank in self.banks:
            with self.subTest(bank=bank["entity_id"]):
                self.assertIs(
                    bank.get("ownership_verified"),
                    False,
                )

    def test_bank_candidates_remain_proposed(self):
        for bank in self.banks:
            with self.subTest(bank=bank["entity_id"]):
                self.assertEqual(
                    bank.get("domain_status"),
                    "proposed",
                )


if __name__ == "__main__":
    unittest.main()
