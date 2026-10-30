#!/usr/bin/env python3
"""
validate-docs.py - Markdown documentation structure, heading, and placeholder validator.

Part of the code-documentation agent skill.
Zero external runtime dependencies (Python 3.10+ standard library).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Directories to ignore by default
DEFAULT_IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode",
}

# Template directories where placeholders are expected by design
TEMPLATE_DIR_NAMES = {"assets", "templates"}

PLACEHOLDER_PATTERN = re.compile(
    r'(?<!`)\b(TODO|FIXME|TBD|CHANGEME|XXX)\b(?![_`])|'
    r'<INSERT[ _A-Z0-9]*>|'
    r'\[INSERT[ _A-Z0-9]*\]|'
    r'\[TODO[ _A-Z0-9]*\]',
    re.IGNORECASE,
)


def validate_markdown_file(file_path: Path, root_path: Path, is_template: bool = False) -> list[dict]:
    """Validate a single markdown file against structure and quality rules."""
    rel_path = str(file_path.relative_to(root_path))
    issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [{
            "file": rel_path,
            "line": 1,
            "severity": "critical",
            "rule": "read_error",
            "message": f"Unable to read file: {e}",
        }]

    # 1. Critical: Empty or near-empty file
    non_whitespace = re.sub(r'\s+', '', content)
    if len(non_whitespace) < 10:
        issues.append({
            "file": rel_path,
            "line": 1,
            "severity": "critical",
            "rule": "empty_file",
            "message": "File is empty or contains fewer than 10 non-whitespace characters.",
        })
        return issues

    lines = content.splitlines()

    # 2. Critical: Check for unclosed code fences
    fence_count = 0
    in_code_fence = False
    fence_char = None
    code_fence_start_line = 0

    code_fence_lines = set()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        fence_match = re.match(r'^(```+|~~~+)', stripped)
        if fence_match:
            current_fence = fence_match.group(1)
            marker = current_fence[0]
            if not in_code_fence:
                in_code_fence = True
                fence_char = marker
                code_fence_start_line = idx
                fence_count += 1
            elif marker == fence_char:
                in_code_fence = False
                fence_char = None
                fence_count += 1

        if in_code_fence:
            code_fence_lines.add(idx)

    if in_code_fence:
        issues.append({
            "file": rel_path,
            "line": code_fence_start_line,
            "severity": "critical",
            "rule": "unclosed_code_fence",
            "message": f"Unclosed code fence starting at line {code_fence_start_line}.",
        })

    # 3. Warning: Missing top-level H1 heading
    has_h1 = any(re.match(r'^#\s+[^#]', line.strip()) for line in lines if not any(line.strip().startswith(p) for p in ("```", "~~~")))
    if not has_h1 and not is_template:
        issues.append({
            "file": rel_path,
            "line": 1,
            "severity": "warning",
            "rule": "missing_h1",
            "message": "Missing top-level H1 header ('# Title').",
        })

    # 4. Warning: Unresolved placeholders (skip inside code blocks, comments, or template files)
    if not is_template:
        for idx, line in enumerate(lines, start=1):
            if idx in code_fence_lines:
                continue

            # Strip inline code from line to avoid flagging documentation about placeholders
            stripped_line = re.sub(r'`[^`]+`', '', line)
            # Strip markdown link destinations to avoid flagging [TODO](...) text
            matches = list(PLACEHOLDER_PATTERN.finditer(stripped_line))
            for m in matches:
                matched_token = m.group(0)
                issues.append({
                    "file": rel_path,
                    "line": idx,
                    "severity": "warning",
                    "rule": "placeholder_detected",
                    "message": f"Unresolved placeholder detected: '{matched_token}'.",
                })

    # 5. Info: Exceptionally long single lines (> 800 characters, potential bundled or minified data)
    for idx, line in enumerate(lines, start=1):
        if len(line) > 800 and not line.strip().startswith("data:"):
            issues.append({
                "file": rel_path,
                "line": idx,
                "severity": "info",
                "rule": "line_too_long",
                "message": f"Line exceeds 800 characters ({len(line)} chars).",
            })

    return issues


def validate_docs(
    target_path: Path,
    extra_ignores: set[str] | None = None,
    check_templates: bool = False,
) -> list[dict]:
    """Validate all markdown documentation in directory or single file."""
    if not target_path.exists():
        raise ValueError(f"Target path does not exist: {target_path}")

    ignores = set(DEFAULT_IGNORE_DIRS)
    if extra_ignores:
        ignores.update(extra_ignores)

    all_issues = []

    if target_path.is_file():
        if target_path.suffix.lower() in (".md", ".markdown"):
            is_template = any(part in TEMPLATE_DIR_NAMES for part in target_path.parts) and not check_templates
            all_issues.extend(validate_markdown_file(target_path, target_path.parent, is_template=is_template))
        return all_issues

    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in ignores and not d.startswith(".")]
        for file in files:
            if file.lower().endswith((".md", ".markdown")):
                file_full = Path(root) / file
                is_template = any(part in TEMPLATE_DIR_NAMES for part in file_full.parts) and not check_templates
                all_issues.extend(validate_markdown_file(file_full, target_path, is_template=is_template))

    return all_issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate Markdown documentation files for structure, headings, and unresolved placeholders."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to markdown file or directory to validate (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as critical failures (exit code 1 on warning)",
    )
    parser.add_argument(
        "--check-templates",
        action="store_true",
        help="Do not skip placeholder checks in template directories",
    )
    parser.add_argument(
        "--ignore",
        help="Comma-separated list of directories to ignore",
    )

    args = parser.parse_args()
    target_path = Path(args.target).resolve()

    extra_ignores = set()
    if args.ignore:
        extra_ignores = {i.strip() for i in args.ignore.split(",") if i.strip()}

    try:
        issues = validate_docs(
            target_path,
            extra_ignores=extra_ignores,
            check_templates=args.check_templates,
        )
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    criticals = [i for i in issues if i["severity"] == "critical"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    infos = [i for i in issues if i["severity"] == "info"]

    if args.format == "json":
        summary = {
            "summary": {
                "critical": len(criticals),
                "warning": len(warnings),
                "info": len(infos),
                "total": len(issues),
            },
            "issues": issues,
        }
        print(json.dumps(summary, indent=2))
    else:
        if not issues:
            print("All documentation files passed validation successfully!")
        else:
            print(f"Validation summary: {len(criticals)} critical, {len(warnings)} warning(s), {len(infos)} info")
            for issue in issues:
                tag = issue["severity"].upper()
                print(f"  [{tag}] {issue['file']}:{issue['line']} ({issue['rule']})")
                print(f"         {issue['message']}")

    if criticals:
        sys.exit(1)
    if args.strict and warnings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
