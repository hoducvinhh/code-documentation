#!/usr/bin/env python3
"""
Unit tests for validate-docs.py.
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

spec = importlib.util.spec_from_file_location("validate_docs_mod", str(SCRIPTS_DIR / "validate-docs.py"))
val_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(val_mod)


class TestValidateDocs(unittest.TestCase):
    def test_valid_document(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc = tmp_path / "doc.md"
            doc.write_text("# Valid Title\n\nThis is a well-formatted document with sufficient content.", encoding="utf-8")

            issues = val_mod.validate_docs(doc)
            self.assertEqual(len(issues), 0)

    def test_empty_document(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc = tmp_path / "empty.md"
            doc.write_text("   \n\n", encoding="utf-8")

            issues = val_mod.validate_docs(doc)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["severity"], "critical")
            self.assertEqual(issues[0]["rule"], "empty_file")

    def test_unclosed_code_fence(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc = tmp_path / "bad_fence.md"
            doc.write_text(
                "# Title\n\n```python\nprint('hello')\n# Notice no closing triple backticks",
                encoding="utf-8",
            )

            issues = val_mod.validate_docs(doc)
            criticals = [i for i in issues if i["severity"] == "critical"]
            self.assertEqual(len(criticals), 1)
            self.assertEqual(criticals[0]["rule"], "unclosed_code_fence")

    def test_missing_h1_header(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc = tmp_path / "no_h1.md"
            doc.write_text("## Only H2 Subheading\n\nContent here without H1.", encoding="utf-8")

            issues = val_mod.validate_docs(doc)
            warnings = [i for i in issues if i["severity"] == "warning"]
            self.assertEqual(len(warnings), 1)
            self.assertEqual(warnings[0]["rule"], "missing_h1")

    def test_placeholder_detected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc = tmp_path / "placeholders.md"
            doc.write_text(
                "# Title\n\nPlease TODO implement this section.\nFollow up <INSERT_URL>.\n",
                encoding="utf-8",
            )

            issues = val_mod.validate_docs(doc)
            placeholders = [i for i in issues if i["rule"] == "placeholder_detected"]
            self.assertEqual(len(placeholders), 2)

    def test_placeholders_in_code_block_ignored(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc = tmp_path / "doc_with_code.md"
            doc.write_text(
                "# Title\n\nInline `TODO` in backticks should not trigger warning.\n\n"
                "```bash\n# TODO in code fence\necho hello\n```\n",
                encoding="utf-8",
            )

            issues = val_mod.validate_docs(doc)
            placeholders = [i for i in issues if i["rule"] == "placeholder_detected"]
            self.assertEqual(len(placeholders), 0)

    def test_template_directory_skips_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            assets_dir = tmp_path / "assets"
            assets_dir.mkdir()
            template_doc = assets_dir / "TEMPLATE.md"
            template_doc.write_text("# Template Title\n\n<INSERT_PROJECT_NAME>\nTODO: fill this in", encoding="utf-8")

            # Normal run: skips placeholders
            issues = val_mod.validate_docs(template_doc)
            self.assertEqual(len(issues), 0)

            # With check_templates=True: flags placeholders
            issues_strict = val_mod.validate_docs(template_doc, check_templates=True)
            self.assertGreater(len(issues_strict), 0)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            good_doc = tmp_path / "good.md"
            good_doc.write_text("# Good Doc\n\nValid content without issues.", encoding="utf-8")

            bad_doc = tmp_path / "empty.md"
            bad_doc.write_text(" ", encoding="utf-8")

            cmd_good = [sys.executable, str(SCRIPTS_DIR / "validate-docs.py"), str(good_doc)]
            res_good = subprocess.run(cmd_good, capture_output=True, text=True)
            self.assertEqual(res_good.returncode, 0)

            cmd_bad = [sys.executable, str(SCRIPTS_DIR / "validate-docs.py"), str(bad_doc)]
            res_bad = subprocess.run(cmd_bad, capture_output=True, text=True)
            self.assertEqual(res_bad.returncode, 1)


if __name__ == "__main__":
    unittest.main()
