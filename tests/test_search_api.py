import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from app.main import Handler


class SearchAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            Handler
        )

        cls.port = cls.server.server_address[1]

        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, path):
        url = f"http://127.0.0.1:{self.port}{path}"

        try:
            with urlopen(url, timeout=5) as response:
                return response.status, json.load(response)
        except HTTPError as exc:
            try:
                return exc.code, json.load(exc)
            finally:
                exc.close()

    def test_health(self):
        status, data = self.request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")

    def test_ministry_search(self):
        status, data = self.request(
            "/api/v1/search?category=ministry"
        )
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 10)

    def test_pagination(self):
        status, data = self.request(
            "/api/v1/search?limit=2&offset=0"
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(data["results"]), 2)

    def test_invalid_category(self):
        status, data = self.request(
            "/api/v1/search?category=invalid"
        )
        self.assertEqual(status, 400)
        self.assertIn("error", data)

    def test_invalid_limit(self):
        status, data = self.request(
            "/api/v1/search?limit=999"
        )
        self.assertEqual(status, 400)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
