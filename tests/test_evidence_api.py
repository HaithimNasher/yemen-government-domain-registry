import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from app.main import Handler


class EvidenceAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            Handler
        )
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.thread.start()
        cls.base = (
            f"http://127.0.0.1:{cls.server.server_port}"
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, path):
        try:
            with urlopen(self.base + path, timeout=5) as response:
                return response.status, json.load(response)
        except HTTPError as exc:
            return exc.code, json.load(exc)

    def test_list_evidence(self):
        status, data = self.request("/api/v1/evidence")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total"], 3)

    def test_filter_evidence(self):
        status, data = self.request(
            "/api/v1/evidence?entity_id=YE-UNI-SANAA"
        )
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 1)
        self.assertEqual(
            data["results"][0]["entity_id"],
            "YE-UNI-SANAA"
        )

    def test_unknown_entity(self):
        status, data = self.request(
            "/api/v1/evidence?entity_id=YE-UNKNOWN"
        )
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 0)

    def test_empty_entity_id(self):
        status, data = self.request(
            "/api/v1/evidence?entity_id="
        )
        self.assertEqual(status, 400)
        self.assertIn("error", data)

    def test_repeated_entity_id(self):
        status, data = self.request(
            "/api/v1/evidence?entity_id=A&entity_id=B"
        )
        self.assertEqual(status, 400)
        self.assertIn("error", data)

    def test_unsupported_parameter(self):
        status, data = self.request(
            "/api/v1/evidence?unexpected=value"
        )
        self.assertEqual(status, 400)
        self.assertIn("error", data)

    def test_ownership_not_verified(self):
        status, data = self.request("/api/v1/evidence")
        self.assertEqual(status, 200)
        for record in data["results"]:
            self.assertFalse(record["ownership_verified"])


if __name__ == "__main__":
    unittest.main()
