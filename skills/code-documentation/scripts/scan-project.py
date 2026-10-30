#!/usr/bin/env python3
"""
scan-project.py - Codebase discovery and metadata extraction script.

Part of the code-documentation agent skill.
Zero external runtime dependencies (Python 3.10+ standard library).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Default directories to ignore during scan
DEFAULT_IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "ENV",
    "__pycache__",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode",
    "coverage",
    ".coverage",
    "bin",
    "obj",
    ".next",
    ".nuxt",
    ".output",
    "vendor",
}

# Extension to language mapping
EXTENSION_LANGUAGE_MAP = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (JSX)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (JSX)",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".scala": "Scala",
    ".md": "Markdown",
    ".markdown": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".ps1": "PowerShell",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
}

# Well-known manifest files and framework hints
MANIFEST_NAMES = {
    "package.json": "Node.js / JavaScript / TypeScript",
    "tsconfig.json": "TypeScript Configuration",
    "pyproject.toml": "Python (PEP 518/621)",
    "requirements.txt": "Python (Pip)",
    "Pipfile": "Python (Pipenv)",
    "setup.py": "Python (Setuptools)",
    "Cargo.toml": "Rust (Cargo)",
    "go.mod": "Go Modules",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java/Kotlin (Gradle)",
    "build.gradle.kts": "Kotlin (Gradle)",
    "composer.json": "PHP (Composer)",
    "Gemfile": "Ruby (Bundler)",
    "mix.exs": "Elixir (Mix)",
}

ENTRY_POINT_PATTERNS = [
    re.compile(r"^(index|main|server|app)\.(ts|js|mjs|py|go|rs|jsx|tsx)$", re.IGNORECASE),
    re.compile(r"^(wsgi|asgi|manage)\.py$", re.IGNORECASE),
    re.compile(r"^src/(index|main|server|app|lib)\.(ts|js|rs|go|py)$", re.IGNORECASE),
    re.compile(r"^app/(main|index|app)\.py$", re.IGNORECASE),
]

DOC_PATTERNS = re.compile(
    r"^(README|CONTRIBUTING|CHANGELOG|LICENSE|SECURITY|ROADMAP|ARCHITECTURE|API|DATABASE)(\.[a-zA-Z0-9]+)?$",
    re.IGNORECASE,
)


def parse_package_json(filepath: Path) -> dict:
    """Extract metadata from package.json."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            deps = list(data.get("dependencies", {}).keys())
            dev_deps = list(data.get("devDependencies", {}).keys())
            scripts = list(data.get("scripts", {}).keys())
            frameworks = []
            all_deps = set(deps + dev_deps)
            if "express" in all_deps:
                frameworks.append("Express")
            if "react" in all_deps:
                frameworks.append("React")
            if "next" in all_deps:
                frameworks.append("Next.js")
            if "vue" in all_deps:
                frameworks.append("Vue")
            if "nestjs" in all_deps or "@nestjs/core" in all_deps:
                frameworks.append("NestJS")
            if "fastify" in all_deps:
                frameworks.append("Fastify")

            return {
                "name": data.get("name", ""),
                "version": data.get("version", ""),
                "description": data.get("description", ""),
                "main": data.get("main", ""),
                "dependencies_count": len(deps),
                "devDependencies_count": len(dev_deps),
                "key_dependencies": deps[:10],
                "scripts": scripts,
                "detected_frameworks": frameworks,
            }
    except Exception as e:
        return {"error": str(e)}


def parse_pyproject_toml(filepath: Path) -> dict:
    """Extract metadata from pyproject.toml without external dependencies."""
    result = {"name": "", "version": "", "detected_frameworks": [], "dependencies": []}
    try:
        content = filepath.read_text(encoding="utf-8")
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if name_match:
            result["name"] = name_match.group(1)
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            result["version"] = version_match.group(1)

        frameworks = []
        lower_content = content.lower()
        if "fastapi" in lower_content:
            frameworks.append("FastAPI")
        if "django" in lower_content:
            frameworks.append("Django")
        if "flask" in lower_content:
            frameworks.append("Flask")
        if "pydantic" in lower_content:
            frameworks.append("Pydantic")
        if "sqlalchemy" in lower_content:
            frameworks.append("SQLAlchemy")
        if "pytest" in lower_content:
            frameworks.append("Pytest")
        result["detected_frameworks"] = frameworks
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def parse_requirements_txt(filepath: Path) -> dict:
    """Extract packages from requirements.txt."""
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
        packages = []
        frameworks = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg = re.split(r"[=<>~!]", line)[0].strip().lower()
            if pkg:
                packages.append(pkg)
                if pkg == "fastapi":
                    frameworks.append("FastAPI")
                elif pkg == "django":
                    frameworks.append("Django")
                elif pkg == "flask":
                    frameworks.append("Flask")
                elif pkg == "pydantic":
                    frameworks.append("Pydantic")
                elif pkg == "sqlalchemy":
                    frameworks.append("SQLAlchemy")
        return {
            "packages_count": len(packages),
            "packages": packages[:15],
            "detected_frameworks": list(set(frameworks)),
        }
    except Exception as e:
        return {"error": str(e)}


def scan_project(root_path: Path, extra_ignores: set[str] | None = None) -> dict:
    """Recursively scan a project directory and collect metadata."""
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError(f"Target path does not exist or is not a directory: {root_path}")

    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    if extra_ignores:
        ignore_dirs.update(extra_ignores)

    manifests = []
    manifest_details = {}
    docs = []
    entry_points = []
    languages_count = {}
    total_files = 0
    scanned_dirs_count = 0
    all_frameworks = set()

    for dirpath_str, dirnames, filenames in os.walk(root_path):
        # Prune ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith(".")]
        scanned_dirs_count += 1
        current_dir = Path(dirpath_str)
        rel_dir = current_dir.relative_to(root_path)

        for filename in filenames:
            total_files += 1
            file_path = current_dir / filename
            rel_file = file_path.relative_to(root_path)
            rel_posix = rel_file.as_posix()

            # Check Manifests
            if filename in MANIFEST_NAMES or filename.endswith(".csproj") or filename.endswith(".sln"):
                manifests.append(rel_posix)
                if filename == "package.json":
                    info = parse_package_json(file_path)
                    manifest_details[rel_posix] = info
                    all_frameworks.update(info.get("detected_frameworks", []))
                elif filename == "pyproject.toml":
                    info = parse_pyproject_toml(file_path)
                    manifest_details[rel_posix] = info
                    all_frameworks.update(info.get("detected_frameworks", []))
                elif filename == "requirements.txt":
                    info = parse_requirements_txt(file_path)
                    manifest_details[rel_posix] = info
                    all_frameworks.update(info.get("detected_frameworks", []))

            # Check Documentation files
            if DOC_PATTERNS.match(filename) or (rel_dir.as_posix().startswith("docs") and filename.endswith(".md")):
                docs.append(rel_posix)

            # Check Entry points
            for pattern in ENTRY_POINT_PATTERNS:
                if pattern.match(filename) or pattern.match(rel_posix):
                    entry_points.append(rel_posix)
                    break

            # Count languages
            ext = file_path.suffix.lower()
            if ext in EXTENSION_LANGUAGE_MAP:
                lang = EXTENSION_LANGUAGE_MAP[ext]
                languages_count[lang] = languages_count.get(lang, 0) + 1

    # Determine primary language
    code_languages = {k: v for k, v in languages_count.items() if k not in ("Markdown", "JSON", "YAML", "TOML", "HTML", "CSS", "SCSS")}
    primary_language = max(code_languages, key=code_languages.get) if code_languages else "Unknown"

    project_name = root_path.resolve().name
    # Override project name if found in manifest
    for detail in manifest_details.values():
        if isinstance(detail, dict) and detail.get("name"):
            project_name = detail["name"]
            break

    return {
        "project_name": project_name,
        "root_path": str(root_path.resolve()),
        "manifests": sorted(manifests),
        "manifest_details": manifest_details,
        "primary_language": primary_language,
        "languages": dict(sorted(languages_count.items(), key=lambda item: item[1], reverse=True)),
        "frameworks": sorted(list(all_frameworks)),
        "documentation_files": sorted(docs),
        "entry_points": sorted(list(set(entry_points))),
        "total_files": total_files,
        "scanned_directories": scanned_dirs_count,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Scan a codebase directory to extract project metadata and documentation status."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to project directory (default: current working directory)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format: json (default) or text",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Path to output file (default: stdout)",
    )
    parser.add_argument(
        "--ignore",
        help="Comma-separated list of additional directory names to ignore",
    )

    args = parser.parse_args()
    target_path = Path(args.target)

    extra_ignores = set()
    if args.ignore:
        extra_ignores = {i.strip() for i in args.ignore.split(",") if i.strip()}

    try:
        data = scan_project(target_path, extra_ignores=extra_ignores)
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    if args.format == "json":
        output_str = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        lines = [
            f"=== Project Analysis: {data['project_name']} ===",
            f"Root Path: {data['root_path']}",
            f"Primary Language: {data['primary_language']}",
            f"Frameworks: {', '.join(data['frameworks']) if data['frameworks'] else 'None detected'}",
            f"Total Files: {data['total_files']} (in {data['scanned_directories']} directories)",
            "",
            "Manifest Files:",
        ]
        for m in data["manifests"]:
            lines.append(f"  - {m}")
        lines.append("")
        lines.append("Detected Entry Points:")
        for ep in data["entry_points"]:
            lines.append(f"  - {ep}")
        lines.append("")
        lines.append("Documentation Files:")
        for doc in data["documentation_files"]:
            lines.append(f"  - {doc}")
        lines.append("")
        lines.append("Language Breakdown:")
        for lang, count in data["languages"].items():
            lines.append(f"  - {lang}: {count} file(s)")
        output_str = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(output_str, encoding="utf-8")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
