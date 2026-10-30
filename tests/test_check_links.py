#!/usr/bin/env python3
"""
Unit tests for check-links.py.
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

spec = importlib.util.spec_from_file_location("check_links_mod", str(SCRIPTS_DIR / "check-links.py"))
check_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_mod)


class TestCheckLinks(unittest.TestCase):
    def test_slugify_heading(self):
        self.assertEqual(check_mod.slugify_heading("Quick Start"), "quick-start")
        self.assertEqual(check_mod.slugify_heading("## 1. Installation & Setup!"), "1-installation--setup")
        self.assertEqual(check_mod.slugify_heading("`code_sample` and [Link](url)"), "code_sample-and-link")

    def test_extract_headings_and_slugs_with_duplicates(self):
        content = """# Main Title
## Overview
## Features
## Features
### Sub-feature
"""
        slugs = check_mod.extract_headings_and_slugs(content)
        self.assertIn("main-title", slugs)
        self.assertIn("overview", slugs)
        self.assertIn("features", slugs)
        self.assertIn("features-1", slugs)
        self.assertIn("sub-feature", slugs)

    def test_valid_internal_and_external_links(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            target_file = tmp_path / "guide.md"
            target_file.write_text("# Guide\n\n## Installation\n\nSteps here.", encoding="utf-8")

            index_file = tmp_path / "index.md"
            index_file.write_text(
                "# Index\n\n"
                "- [Guide](guide.md)\n"
                "- [Guide Install](guide.md#installation)\n"
                "- [External](https://example.com)\n"
                "- [Mail](mailto:user@example.com)\n",
                encoding="utf-8",
            )

            issues = check_mod.validate_links(index_file)
            self.assertEqual(len(issues), 0)

    def test_broken_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            index_file = tmp_path / "index.md"
            index_file.write_text("# Index\n\n[Missing](non_existent_file.md)\n", encoding="utf-8")

            issues = check_mod.validate_links(index_file)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["type"], "broken_path")
            self.assertIn("non_existent_file.md", issues[0]["target"])

    def test_broken_heading_anchor(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            index_file = tmp_path / "index.md"
            index_file.write_text("# Index\n\n[Bad Anchor](#missing-heading)\n", encoding="utf-8")

            issues = check_mod.validate_links(index_file)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["type"], "broken_anchor")
            self.assertEqual(issues[0]["target"], "#missing-heading")

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            good_file = tmp_path / "good.md"
            good_file.write_text("# Good\n\n[Good](https://example.com)\n", encoding="utf-8")

            bad_file = tmp_path / "bad.md"
            bad_file.write_text("# Bad\n\n[Bad](missing.md)\n", encoding="utf-8")

            cmd_good = [sys.executable, str(SCRIPTS_DIR / "check-links.py"), str(good_file)]
            res_good = subprocess.run(cmd_good, capture_output=True, text=True)
            self.assertEqual(res_good.returncode, 0)

            cmd_bad = [sys.executable, str(SCRIPTS_DIR / "check-links.py"), str(bad_file)]
            res_bad = subprocess.run(cmd_bad, capture_output=True, text=True)
            self.assertEqual(res_bad.returncode, 1)

    def test_links_inside_code_fence_ignored(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            index_file = tmp_path / "index.md"
            index_file.write_text(
                "# Code Fence Test\n\n```markdown\n[Example](nonexistent-file.md)\n```\n",
                encoding="utf-8",
            )
            issues = check_mod.validate_links(index_file)
            self.assertEqual(len(issues), 0)

    def test_links_inside_inline_code_ignored(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            index_file = tmp_path / "index.md"
            index_file.write_text(
                "# Inline Code Test\n\nUse `[Example](nonexistent-file.md)` to format links.\n",
                encoding="utf-8",
            )
            issues = check_mod.validate_links(index_file)
            self.assertEqual(len(issues), 0)

    def test_template_directory_skips_links(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            assets_dir = tmp_path / "assets"
            assets_dir.mkdir()
            template_file = assets_dir / "TEMPLATE.md"
            template_file.write_text(
                "# Template\n\n[License](LICENSE)\n",
                encoding="utf-8",
            )
            # By default skips template files
            issues = check_mod.validate_links(template_file)
            self.assertEqual(len(issues), 0)

            # With check_templates=True, flags missing LICENSE
            issues_strict = check_mod.validate_links(template_file, check_templates=True)
            self.assertEqual(len(issues_strict), 1)


if __name__ == "__main__":
    unittest.main()
