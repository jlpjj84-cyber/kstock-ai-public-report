"""Tests that never access the private repository or the network."""
import json
import unittest

from scripts.mirror_report import validate, scan_keys, page


class MirrorSafetyTests(unittest.TestCase):
    def test_accepts_public_report(self):
        text = "KStock AI 공개 성능 리포트\n자료 기준일: 2026-11-12\n"
        data = {"title": "KStock", "performance": {"return_pct": 3.24}}
        out_text, out_json = validate(text.encode(), json.dumps(data).encode())
        self.assertEqual(out_text, text)
        self.assertEqual(out_json, data)

    def test_rejects_secret_field_recursive(self):
        text = "KStock\n자료 기준일"
        for bad in ("access_token", "app_secret", "order_no", "positions"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate(text.encode(),
                             json.dumps({"nested": [{bad: "SECRET"}]}).encode())

    def test_rejects_bearer_token_values_even_without_secret_key(self):
        with self.assertRaises(ValueError):
            validate(
                b"KStock\n" + "자료 기준일".encode(),
                json.dumps({"description": "Bearer abcdefghijklmnopqrstuvwxyz"}).encode(),
            )

    def test_rejects_html_login_response(self):
        with self.assertRaises(ValueError):
            validate(b"<!doctype html><title>KStock</title>资料", b'{"ok":true}')

    def test_rejects_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            validate("KStock\n자료 기준일".encode(), b"not json")

    def test_page_escapes_untrusted_body_by_text_content_only(self):
        html = page()
        self.assertIn("box.textContent=await response.text()", html)
        self.assertNotIn("innerHTML", html)

if __name__ == "__main__":
    unittest.main()
