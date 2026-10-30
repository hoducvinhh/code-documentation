# Documentation Quality Checklist & Severity Matrix

## Overview

Use this checklist to perform final sign-off on generated or revised technical documentation. Every document must satisfy the baseline quality criteria before delivery.

---

## 1. Severity Levels

| Severity | Description | Action Required |
| :--- | :--- | :--- |
| **Critical** | Major defect that misleads developers, breaks builds, or compromises security. | Must be fixed immediately. Blocks sign-off. |
| **Warning** | Minor omission, incomplete placeholder, or formatting flaw that reduces quality. | Should be fixed before merging or publication. |
| **Informational** | Stylistic suggestions or minor optimization notes. | Optional cleanup. |

---

## 2. Quality Rubric

### A. Correctness & Evidence (Critical)
- [ ] Every API endpoint, route path, and HTTP method exists in source code.
- [ ] Every environment variable matches actual code lookups (`process.env.X` / `os.getenv("X")`).
- [ ] Prerequisites (Node version, Python version, DB engine) reflect project manifests.
- [ ] Commands listed in Quickstart match commands defined in `package.json` or `Makefile`.

### B. Security & Credentials (Critical)
- [ ] Zero real API tokens, JWTs, AWS credentials, or private keys in documents.
- [ ] Sanitized credentials used in examples (`postgres://user:password@localhost:5432/mydb`).
- [ ] Secret detection script passes with exit code `0`.

### C. Structure & Markdown Integrity (Critical / Warning)
- [ ] Exactly one H1 heading at the top of the file.
- [ ] All code fences are closed and annotated with the appropriate language identifier.
- [ ] Tables are formatted with correct column counts.
- [ ] Zero uncompleted placeholders (`TODO`, `FIXME`, `<INSERT_HERE>`).

### D. Navigation & Links (Warning)
- [ ] All relative file links resolve to existing files on disk.
- [ ] All in-page heading anchors resolve to existing headings.
- [ ] External URLs use `https://`.
- [ ] Link verification script passes with exit code `0`.

### E. Readability & Maintenance (Informational)
- [ ] Clear executive summary / overview paragraph.
- [ ] Diagrams (Mermaid) render cleanly and explain complex workflows.
- [ ] Consistent tone (active voice, concise, professional).
