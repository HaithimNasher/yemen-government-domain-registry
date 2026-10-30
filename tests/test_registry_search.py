import json
from pathlib import Path

expected_ministries = len(json.loads(
    (Path(__file__).resolve().parent.parent / "data" / "ministries.json")
    .read_text(encoding="utf-8")
))

import unittest

from app.registry_search import search_entities


class RegistrySearchTests(unittest.TestCase):

    def test_ministry_count(self):
        result = search_entities(category="ministry")
        self.assertEqual(result["total"], expected_ministries)

    def test_university_count(self):
        result = search_entities(category="university")
        self.assertEqual(result["total"], 3)

    def test_pagination(self):
        result = search_entities(limit=5)
        self.assertEqual(len(result["results"]), 5)

    def test_invalid_category(self):
        with self.assertRaises(ValueError):
            search_entities(category="invalid")

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            search_entities(limit=1000)


if __name__ == "__main__":
    unittest.main()
