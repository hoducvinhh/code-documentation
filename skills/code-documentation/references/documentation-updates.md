# Documentation Updates & Drift Detection Guide

## Overview

Software evolves constantly. Documentation drift occurs when source code is added, modified, or deleted without corresponding updates to documentation. This guide outlines how to audit, maintain, and surgically update documentation over time.

---

## 1. Detecting Documentation Drift

To determine whether documentation has drifted from the current codebase:

1. **Inspect Git History**:
   ```bash
   git diff --stat HEAD~5..HEAD
   ```
   Identify modified route handlers, renamed models, new environment variables, or dependency changes.

2. **Cross-Check API Routes**:
   Compare routes listed in `API.md` against routes declared in the code.
   - Any missing endpoints?
   - Any removed endpoints still documented?
   - Any updated request/response fields?

3. **Cross-Check Environment Variables**:
   Compare variables in `README.md` / `config` against actual `os.getenv` or `process.env` calls.

---

## 2. Surgical (Non-Destructive) Updates

When updating documentation:
- **Never wipe out existing files completely** unless instructed by the user or starting from a completely blank repository.
- **Preserve Human-Written Sections**: Developer tutorials, custom domain explanations, and manual architecture notes should be kept intact.
- **Update Only What Changed**:
  - Add newly created endpoints to the relevant section.
  - Update signatures or schemas that changed.
  - Deprecate removed endpoints with a clear note rather than breaking external links if consumers still reference them.

---

## 3. Maintenance Audit Checklist

Before releasing documentation updates:
- [ ] Run `scan-project.py` to verify package versions and script definitions.
- [ ] Run `check-links.py` to ensure no internal links were broken by renamed sections.
- [ ] Run `validate-docs.py` to confirm no temporary placeholders remain.
- [ ] Run `detect-secrets.py` to verify no credentials leaked.
