#!/usr/bin/env python3
"""
Unit tests for detect-secrets.py.
Part of code-documentation agent skill.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "code-documentation" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

spec = importlib.util.spec_from_file_location("detect_secrets_mod", str(SCRIPTS_DIR / "detect-secrets.py"))
sec_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sec_mod)


class TestDetectSecrets(unittest.TestCase):
    def test_redact_function(self):
        secret = "ghp_1234567890abcdef1234567890abcdef1234"
        masked = sec_mod.redact(secret)
        self.assertNotIn("1234567890abcdef", masked)
        self.assertTrue("*" in masked)
        self.assertTrue(masked.startswith("ghp_"))
        self.assertTrue(masked.endswith("234"))

    def test_detect_aws_access_key(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            f = tmp_path / "creds.py"
            # Genuine format AWS key: AKIA + 16 alphanumeric characters without placeholder words
            f.write_text("AWS_KEY = 'AKIAIOSFODNN7BCDFGHJ'\n", encoding="utf-8")

            findings = sec_mod.scan_file(f, tmp_path)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["rule"], "AWS Access Key ID")
            self.assertIn("*", findings[0]["redacted_secret"])

    def test_detect_github_token(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            f = tmp_path / "config.ts"
            token = "ghp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8"
            f.write_text(f"const token = '{token}';\n", encoding="utf-8")

            findings = sec_mod.scan_file(f, tmp_path)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["rule"], "GitHub Token")
            self.assertIn("*", findings[0]["redacted_secret"])

    def test_detect_private_key(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            f = tmp_path / "server.key"
            f.write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----\n", encoding="utf-8")

            findings = sec_mod.scan_file(f, tmp_path)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["rule"], "Private Key")

    def test_safe_placeholders_not_flagged(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            f = tmp_path / "README.md"
            f.write_text(
                "# Config\n\n"
                "Set API_KEY='your_api_key_here'\n"
                "export SECRET_KEY='dummy_secret_placeholder'\n"
                "STRIPE_KEY='sk_test_xxx'\n",
                encoding="utf-8",
            )

            findings = sec_mod.scan_file(f, tmp_path)
            self.assertEqual(len(findings), 0)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            safe_file = tmp_path / "safe.md"
            safe_file.write_text("# Documentation\nNo secrets here.\n", encoding="utf-8")

            leak_file = tmp_path / "leak.py"
            leak_file.write_text("TOKEN = 'ghp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8'\n", encoding="utf-8")

            cmd_safe = [sys.executable, str(SCRIPTS_DIR / "detect-secrets.py"), str(safe_file)]
            res_safe = subprocess.run(cmd_safe, capture_output=True, text=True)
            self.assertEqual(res_safe.returncode, 0)

            cmd_leak = [sys.executable, str(SCRIPTS_DIR / "detect-secrets.py"), str(leak_file)]
            res_leak = subprocess.run(cmd_leak, capture_output=True, text=True)
            self.assertEqual(res_leak.returncode, 1)


if __name__ == "__main__":
    unittest.main()
