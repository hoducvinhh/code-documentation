#!/usr/bin/env python3
"""
detect-secrets.py - Secret detection and redaction scanner.

Part of the code-documentation agent skill.
Zero external runtime dependencies (Python 3.10+ standard library).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Directories to ignore
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
    "__pycache__",
}

# Known placeholder / safe words that are not real secrets
PLACEHOLDER_SUBSTRINGS = {
    "example",
    "placeholder",
    "dummy",
    "your_api_key",
    "your-api-key",
    "my_secret",
    "changeme",
    "insert_",
    "replace_me",
    "fake",
    "mock",
    "sample",
    "test_key",
    "sk_test_xxx",
    "sk_live_xxx",
    "xxxx",
    "000000",
    "12345678",
    "abcdef",
}

# Detection rules: (Rule Name, Compiled Regex)
RULES = [
    (
        "Private Key",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ),
    (
        "AWS Access Key ID",
        re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),
    ),
    (
        "GitHub Token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
    ),
    (
        "Slack Token",
        re.compile(r"\bxox[baprs]-[0-9a-zA-Z-]{10,}\b"),
    ),
    (
        "Stripe Secret Key",
        re.compile(r"\b(?:sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,}\b"),
    ),
    (
        "Database Connection String with Password",
        re.compile(
            r"(?i)\b(?:postgres|postgresql|mysql|mongodb|redis):\/\/[a-zA-Z0-9_\-\.]+:(?!(?:password|pass|<.*>|\${.*}))([^@\s\"'\n]+)@[a-zA-Z0-9_\-\.]+"
        ),
    ),
    (
        "Generic High-Entropy Secret Assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*[\"']([A-Za-z0-9_\-\.]{24,})[\"']"
        ),
    ),
]


def redact(secret: str) -> str:
    """Redact secret string showing only prefix and suffix if long enough."""
    secret = secret.strip()
    if len(secret) <= 8:
        return "[REDACTED]"
    prefix_len = min(4, len(secret) // 4)
    suffix_len = min(3, len(secret) // 4)
    masked_len = len(secret) - prefix_len - suffix_len
    return secret[:prefix_len] + ("*" * masked_len) + secret[-suffix_len:]


def is_placeholder(matched_str: str) -> bool:
    """Check if matched string is an obvious documentation placeholder or dummy string."""
    lower = matched_str.lower()
    for ph in PLACEHOLDER_SUBSTRINGS:
        if ph in lower:
            return True
    # Check if mostly repetitive chars (e.g. 1111111111, aaaaaaaaaa)
    if len(set(lower)) <= 3:
        return True
    return False


def scan_file(file_path: Path, root_path: Path) -> list[dict]:
    """Scan a single file for exposed secrets."""
    rel_path = str(file_path.relative_to(root_path))
    findings = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return []

    lines = content.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        # Skip regex definition lines inside detect-secrets.py or tests itself to avoid self-flagging
        if "detect-secrets" in rel_path or "test_detect_secrets" in rel_path:
            continue

        for rule_name, pattern in RULES:
            for match in pattern.finditer(line):
                full_match = match.group(0)
                if rule_name in ("Generic High-Entropy Secret Assignment", "Database Connection String with Password"):
                    secret_candidate = match.group(1) if match.lastindex and match.lastindex >= 1 else full_match
                else:
                    secret_candidate = full_match

                if is_placeholder(secret_candidate):
                    continue

                findings.append({
                    "file": rel_path,
                    "line": line_idx,
                    "rule": rule_name,
                    "redacted_secret": redact(secret_candidate),
                    "context_preview": redact(line.strip()),
                })

    return findings


def scan_for_secrets(target_path: Path, extra_ignores: set[str] | None = None) -> list[dict]:
    """Scan directory or file for secrets."""
    if not target_path.exists():
        raise ValueError(f"Target path does not exist: {target_path}")

    ignores = set(DEFAULT_IGNORE_DIRS)
    if extra_ignores:
        ignores.update(extra_ignores)

    all_findings = []

    if target_path.is_file():
        return scan_file(target_path, target_path.parent)

    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in ignores and not d.startswith(".")]
        for file in files:
            file_path = Path(root) / file
            # Only scan text-like files, skip compiled and media files
            if file_path.suffix.lower() in (
                ".py", ".ts", ".js", ".md", ".json", ".yaml", ".yml", ".toml",
                ".env", ".txt", ".sh", ".rs", ".go", ".java", ".xml", ".html",
            ):
                all_findings.extend(scan_file(file_path, target_path))

    return all_findings


def main():
    parser = argparse.ArgumentParser(
        description="Scan code and documentation files for accidentally leaked secrets and tokens."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to file or directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json",
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
        findings = scan_for_secrets(target_path, extra_ignores=extra_ignores)
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    if args.format == "json":
        print(json.dumps({"total_findings": len(findings), "findings": findings}, indent=2))
    else:
        if not findings:
            print("No exposed secrets or credentials detected. Safe to publish!")
        else:
            print(f"SECURITY ALERT: Found {len(findings)} potential secret(s):")
            for f in findings:
                print(f"  [SECRET] {f['file']}:{f['line']} - {f['rule']}")
                print(f"           Redacted: {f['redacted_secret']}")

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
