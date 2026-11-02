#!/usr/bin/env python3
"""
check-links.py - Markdown link and heading anchor integrity validator.

Part of the code-documentation agent skill.
Zero external runtime dependencies (Python 3.10+ standard library).
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

# Regex for Markdown links: [text](url) and ![alt](url)
MARKDOWN_LINK_PATTERN = re.compile(r'!?\[([^\]]*)\]\(([^)]+)\)')

# External schemes to ignore
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "ftp://", "data:", "tel:", "file://", "conversation://")

# Markdown heading pattern
HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

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

TEMPLATE_DIR_NAMES = {"assets", "templates"}


def slugify_heading(heading_text: str) -> str:
    """
    Generate a GitHub-compatible markdown heading anchor slug.
    Example: '## 1. Quick Start & Setup!' -> '1-quick-start--setup'
    """
    # Strip leading markdown hashes if full heading line is passed
    cleaned = re.sub(r'^#+\s*', '', heading_text.strip())
    # Strip inline code formatting, bold/italics (backticks, asterisks, tildes)
    cleaned = re.sub(r'[`*~]', '', cleaned)
    # Remove markdown links inside heading: [text](link) -> text
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
    # Lowercase
    cleaned = cleaned.strip().lower()
    # Replace whitespace with hyphens
    cleaned = re.sub(r'\s+', '-', cleaned)
    # Remove punctuation characters not allowed in GitHub slugs
    # GitHub preserves letters, numbers, hyphens, underscores, and unicode alphanumeric
    cleaned = re.sub(r'[^\w\-]', '', cleaned)
    return cleaned


def extract_headings_and_slugs(content: str) -> set[str]:
    """Extract all heading anchor slugs from markdown content, handling duplicates."""
    slug_counts: dict[str, int] = {}
    valid_slugs: set[str] = set()

    for match in HEADING_PATTERN.finditer(content):
        heading_text = match.group(2).strip()
        base_slug = slugify_heading(heading_text)
        if not base_slug:
            continue

        if base_slug in slug_counts:
            slug_counts[base_slug] += 1
            slug_with_suffix = f"{base_slug}-{slug_counts[base_slug]}"
            valid_slugs.add(slug_with_suffix)
        else:
            slug_counts[base_slug] = 0
            valid_slugs.add(base_slug)

    return valid_slugs


def check_file_links(file_path: Path, root_path: Path) -> list[dict]:
    """Check all markdown links in a single file."""
    issues = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [{
            "file": str(file_path.relative_to(root_path)),
            "line": 1,
            "type": "file_read_error",
            "message": f"Unable to read file: {e}",
        }]

    # Cache headings for the current file
    current_file_slugs = None
    # Cache headings for external referenced files
    other_file_slugs_cache: dict[Path, set[str]] = {}

    lines = content.splitlines()
    in_code_fence = False
    fence_char = None

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        fence_match = re.match(r'^(```+|~~~+)', stripped)
        if fence_match:
            marker = fence_match.group(1)[0]
            if not in_code_fence:
                in_code_fence = True
                fence_char = marker
            elif marker == fence_char:
                in_code_fence = False
                fence_char = None
            continue

        if in_code_fence:
            continue

        # Find spans of inline code: `...`
        code_spans = [m.span() for m in re.finditer(r'`+[^`]+`+', line)]

        for match in MARKDOWN_LINK_PATTERN.finditer(line):
            start_pos, end_pos = match.span()
            # If the link match is enclosed within an inline code span, skip it
            if any(cs[0] <= start_pos and end_pos <= cs[1] for cs in code_spans):
                continue

            link_text = match.group(1).strip()
            raw_target = match.group(2).strip()

            # Ignore angle-bracket placeholders or template variables like <url> or {{url}}
            if raw_target.startswith("<") and raw_target.endswith(">"):
                continue
            if raw_target.startswith("{{") or raw_target.startswith("${"):
                continue

            # Strip optional title in link: [text](path "title")
            target = raw_target.split()[0].strip('"').strip("'")

            # Check if external URL or protocol
            if any(target.startswith(scheme) for scheme in EXTERNAL_SCHEMES):
                continue

            # Check for anchor only: `#heading`
            if target.startswith("#"):
                anchor = urllib.parse.unquote(target[1:])
                if not anchor:
                    continue
                if current_file_slugs is None:
                    current_file_slugs = extract_headings_and_slugs(content)

                if anchor not in current_file_slugs:
                    issues.append({
                        "file": str(file_path.relative_to(root_path)),
                        "line": line_num,
                        "type": "broken_anchor",
                        "target": target,
                        "text": link_text,
                        "message": f"Anchor '#{anchor}' does not match any heading in the document.",
                    })
                continue

            # File path with optional anchor: `other.md#heading`
            parts = target.split("#", 1)
            file_part = urllib.parse.unquote(parts[0])
            anchor_part = urllib.parse.unquote(parts[1]) if len(parts) > 1 else None

            # Resolve relative path from current file's directory
            resolved_target = Path(os.path.abspath(file_path.parent / file_part))

            if not resolved_target.exists():
                issues.append({
                    "file": str(file_path.relative_to(root_path)),
                    "line": line_num,
                    "type": "broken_path",
                    "target": target,
                    "text": link_text,
                    "message": f"Referenced file does not exist: {file_part}",
                })
            elif anchor_part and resolved_target.suffix.lower() in (".md", ".markdown"):
                # Verify anchor in the target file
                if resolved_target not in other_file_slugs_cache:
                    try:
                        target_content = resolved_target.read_text(encoding="utf-8")
                        other_file_slugs_cache[resolved_target] = extract_headings_and_slugs(target_content)
                    except Exception:
                        other_file_slugs_cache[resolved_target] = set()

                if anchor_part not in other_file_slugs_cache[resolved_target]:
                    issues.append({
                        "file": str(file_path.relative_to(root_path)),
                        "line": line_num,
                        "type": "broken_anchor",
                        "target": target,
                        "text": link_text,
                        "message": f"Anchor '#{anchor_part}' not found in target file: {file_part}",
                    })

    return issues


def validate_links(
    target_path: Path,
    ignore_dirs: set[str] | None = None,
    check_templates: bool = False,
) -> list[dict]:
    """Validate links across all markdown files in target path or single file."""
    if not target_path.exists():
        raise ValueError(f"Path does not exist: {target_path}")

    ignores = set(DEFAULT_IGNORE_DIRS)
    if ignore_dirs:
        ignores.update(ignore_dirs)

    all_issues = []

    if target_path.is_file():
        if target_path.suffix.lower() in (".md", ".markdown"):
            is_template = any(part in TEMPLATE_DIR_NAMES for part in target_path.parts)
            if not is_template or check_templates:
                all_issues.extend(check_file_links(target_path, target_path.parent))
        return all_issues

    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in ignores and not d.startswith(".")]
        for file in files:
            if file.lower().endswith((".md", ".markdown")):
                file_full = Path(root) / file
                is_template = any(part in TEMPLATE_DIR_NAMES for part in file_full.parts)
                if is_template and not check_templates:
                    continue
                all_issues.extend(check_file_links(file_full, target_path))

    return all_issues


def main():
    parser = argparse.ArgumentParser(
        description="Verify relative paths and heading anchors in Markdown files."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to markdown file or directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json",
    )
    parser.add_argument(
        "--check-templates",
        action="store_true",
        help="Do not skip link validation in template directories (assets/templates)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only display output if broken links are detected",
    )

    args = parser.parse_args()
    target_path = Path(os.path.abspath(args.target))

    try:
        issues = validate_links(target_path, check_templates=args.check_templates)
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    if args.format == "json":
        print(json.dumps({"total_issues": len(issues), "issues": issues}, indent=2))
    else:
        if not issues:
            if not args.quiet:
                print("All markdown links and heading anchors are valid!")
        else:
            print(f"Found {len(issues)} broken link issue(s):")
            for issue in issues:
                print(f"  [{issue['type'].upper()}] {issue['file']}:{issue['line']}")
                print(f"     Target: {issue.get('target', 'N/A')}")
                print(f"     Message: {issue['message']}")

    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
