import unittest

from scripts.add_source_candidate import validate_url


class SourceCandidateTests(unittest.TestCase):

    def test_valid_https(self):
        url = "https://example.org/about"
        self.assertEqual(validate_url(url), url)

    def test_reject_file_url(self):
        with self.assertRaises(ValueError):
            validate_url("file:///etc/passwd")

    def test_reject_localhost(self):
        with self.assertRaises(ValueError):
            validate_url("http://localhost/test")

    def test_reject_private_ip(self):
        with self.assertRaises(ValueError):
            validate_url("http://192.168.1.1/test")

    def test_reject_credentials(self):
        with self.assertRaises(ValueError):
            validate_url("https://user:pass@example.org")

    def test_reject_invalid_port(self):
        with self.assertRaises(ValueError):
            validate_url("https://example.org:99999")

    def test_reject_whitespace(self):
        with self.assertRaises(ValueError):
            validate_url(" https://example.org ")


if __name__ == "__main__":
    unittest.main()
