# Documentation Standards & Style Guide

## Overview

High-quality documentation is clear, concise, structurally sound, and accessible. This document establishes technical writing standards for markdown documents produced by the `code-documentation` agent skill.

---

## 1. Markdown Syntax Rules

### Headings
- Exactly **one** top-level H1 (`# Title`) per document.
- Follow a strict logical hierarchy: H1 -> H2 -> H3 -> H4. Never skip levels (e.g. avoid H1 directly followed by H3).
- Use sentence or title case consistently.
- Headings should be anchor-friendly: avoid raw punctuation or emojis in headings that might disrupt URL slug generation.

### Code Blocks
- Always specify the language identifier on fenced code blocks:
  ```markdown
  ```typescript
  const message: string = "Hello World";
  ```
  ```
- Use `bash` or `sh` for shell commands.
- Use `json`, `yaml`, `toml` for structured data.
- Use `mermaid` for diagram blocks.
- Never leave an unclosed code block (an odd number of backtick fences will break rendering).

### Tables
- Format tables with clear header rows and alignment indicators:
  ```markdown
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `id` | `string` | Yes | Unique identifier |
  ```
- Ensure every row has matching column counts.

### Links
- All internal cross-references must use relative file paths: `[Architecture Guide](ARCHITECTURE.md)` or `[Config Guide](docs/config.md#database)`.
- Use GitHub-compatible anchor slugs for in-page navigation:
  - Example heading: `## 3. Getting Started` -> `#3-getting-started`
  - Example heading: `### Environment Setup & Config` -> `#environment-setup--config`
- Validate all links with `check-links.py` before finalizing documents.

---

## 2. Technical Writing Tone & Style

1. **Active Voice & Imperative Mood**:
   - Prefer: *"Run the migration script to apply changes."*
   - Avoid: *"The migration script should be run by the user in order to apply changes."*
2. **Concise and Objective**:
   - Provide direct instructions and facts. Avoid filler phrases ("Please note that...", "It goes without saying that...").
3. **No Hallucinated Parameters**:
   - If a parameter, header, or configuration option is not verified in code, do not invent it.
   - Use `[TBD: Needs confirmation from team]` if a critical detail is unverified.
4. **Redact Sensitive Information**:
   - Never embed real secrets, passwords, or production tokens in documentation examples.
   - Use sanitized values like `your-api-key-here` or `postgres://user:password@localhost:5432/dbname`.

---

## 3. Standard Document Layout

Every major documentation file should adhere to the following outline:

1. **H1 Title**: Name of the component, service, or concept.
2. **Badges / Metadata**: Version, build status, license, language indicators.
3. **Table of Contents**: For documents longer than 100 lines.
4. **Overview**: Executive summary explaining what the project is and why it exists.
5. **Core Content**: Architecture, API references, configuration tables, or workflows.
6. **Troubleshooting / Verification**: How to test, verify, and diagnose issues.
7. **References**: Links to related files and external specifications.
