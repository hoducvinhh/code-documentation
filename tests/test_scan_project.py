#!/usr/bin/env python3
"""
Unit tests for scan-project.py.
Part of code-documentation agent skill.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path for direct import
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "code-documentation" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util

spec = importlib.util.spec_from_file_location("scan_project_mod", str(SCRIPTS_DIR / "scan-project.py"))
scan_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan_mod)


class TestScanProject(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = Path(__file__).resolve().parent / "fixtures"
        self.nodejs_dir = self.fixtures_dir / "nodejs-typescript"
        self.python_dir = self.fixtures_dir / "python"

    def test_scan_nodejs_typescript_fixture(self):
        result = scan_mod.scan_project(self.nodejs_dir)
        self.assertEqual(result["project_name"], "sample-express-service")
        self.assertEqual(result["primary_language"], "TypeScript")
        self.assertIn("package.json", result["manifests"])
        self.assertIn("tsconfig.json", result["manifests"])
        self.assertIn("Express", result["frameworks"])
        self.assertIn("src/index.ts", result["entry_points"])
        self.assertIn("README.md", result["documentation_files"])
        self.assertGreater(result["total_files"], 0)

    def test_scan_python_fixture(self):
        result = scan_mod.scan_project(self.python_dir)
        self.assertEqual(result["project_name"], "sample-fastapi-service")
        self.assertEqual(result["primary_language"], "Python")
        self.assertIn("pyproject.toml", result["manifests"])
        self.assertIn("requirements.txt", result["manifests"])
        self.assertIn("FastAPI", result["frameworks"])
        self.assertIn("Pydantic", result["frameworks"])
        self.assertIn("app/main.py", result["entry_points"])

    def test_scan_nonexistent_directory(self):
        with self.assertRaises(ValueError):
            scan_mod.scan_project(Path("non_existent_directory_12345"))

    def test_ignore_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Normal file
            (tmp_path / "valid.py").write_text("print('hello')", encoding="utf-8")
            # Ignored folder
            node_modules = tmp_path / "node_modules"
            node_modules.mkdir()
            (node_modules / "ignored.js").write_text("console.log('ignored')", encoding="utf-8")
            venv_dir = tmp_path / ".venv"
            venv_dir.mkdir()
            (venv_dir / "ignored.py").write_text("pass", encoding="utf-8")

            result = scan_mod.scan_project(tmp_path)
            self.assertEqual(result["total_files"], 1)
            self.assertEqual(result["primary_language"], "Python")

    def test_cli_execution_json(self):
        cmd = [sys.executable, str(SCRIPTS_DIR / "scan-project.py"), str(self.nodejs_dir), "--format", "json"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        parsed = json.loads(proc.stdout)
        self.assertEqual(parsed["project_name"], "sample-express-service")

    def test_cli_execution_text(self):
        cmd = [sys.executable, str(SCRIPTS_DIR / "scan-project.py"), str(self.nodejs_dir), "--format", "text"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Project Analysis: sample-express-service", proc.stdout)


if __name__ == "__main__":
    unittest.main()
