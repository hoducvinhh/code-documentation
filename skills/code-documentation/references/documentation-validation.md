# Documentation Validation Guide

## Overview

Documentation validation is a mandatory automated quality assurance step. Never assume that generated or edited markdown documents are free of flaws. This guide covers how to execute, interpret, and resolve issues flagged by the validation toolchain.

---

## 1. The Validation Pipeline

The validation pipeline consists of 3 distinct stages:

```mermaid
flowchart LR
    Docs["Target Documentation"] --> Links["1. Link Validation<br>(check-links.py)"]
    Links --> Structure["2. Structure & Linter<br>(validate-docs.py)"]
    Structure --> Secrets["3. Secret Scanning<br>(detect-secrets.py)"]
    Secrets --> Result["Verified Documentation"]
```

---

## 2. Stage 1: Link and Anchor Integrity (`check-links.py`)

Verifies all relative file paths and heading anchor links across markdown documents.

### Running Link Checks
```bash
python skills/code-documentation/scripts/check-links.py <PROJECT_DIR>
```

### Common Issues & Remediations
1. **Broken Relative Path**:
   - *Message*: `Referenced file does not exist: docs/setup.md`
   - *Fix*: Check the actual file location and adjust relative path depth (e.g., `../docs/setup.md`).
2. **Broken Heading Anchor**:
   - *Message*: `Anchor '#quick-start' does not match any heading in the document.`
   - *Fix*: Ensure the heading text matches the anchor slug. Remember that punctuation is stripped and spaces become single hyphens (e.g. `## 1. Quick Start!` -> `#1-quick-start`).
3. **Target File Anchor Mismatch**:
   - *Message*: `Anchor '#config' not found in target file: ARCHITECTURE.md`
   - *Fix*: Verify that the target document has a corresponding heading.

---

## 3. Stage 2: Structural & Quality Linting (`validate-docs.py`)

Checks formatting integrity, heading hierarchy, and unresolved placeholders.

### Running Structure Validation
```bash
python skills/code-documentation/scripts/validate-docs.py <PROJECT_DIR>
```

### Common Issues & Remediations
1. **Empty File (`empty_file`)**:
   - *Severity*: Critical
   - *Fix*: Complete the document or remove the orphaned placeholder file.
2. **Unclosed Code Fence (`unclosed_code_fence`)**:
   - *Severity*: Critical
   - *Fix*: Add matching closing triple backticks (```` ``` ````) to close the block.
3. **Missing H1 Header (`missing_h1`)**:
   - *Severity*: Warning
   - *Fix*: Add a single `# Document Title` at the beginning of the file.
4. **Unresolved Placeholder (`placeholder_detected`)**:
   - *Severity*: Warning
   - *Fix*: Replace `TODO`, `FIXME`, or `<INSERT_...>` with concrete technical information or remove the placeholder.

---

## 4. Stage 3: Secret Detection (`detect-secrets.py`)

Ensures no private keys, database credentials, or API tokens were accidentally committed to markdown documents.

### Running Secret Scan
```bash
python skills/code-documentation/scripts/detect-secrets.py <PROJECT_DIR>
```

### Remediations
- Replace any real secret with placeholder variables (e.g. `your-api-key-here` or `DATABASE_URL=postgres://user:password@localhost:5432/dbname`).
- If an actual credential was already committed, alert the team immediately to revoke and rotate the secret.
