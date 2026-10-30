# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-30

### Added
- Initial release of `code-documentation` skill adhering to the Agent Skills Specification (1.0).
- Core skill definition file `skills/code-documentation/SKILL.md` with an 8-step documentation workflow.
- 4 zero-dependency Python 3 standard library helper scripts:
  - `scan-project.py`: Project discovery, manifest detection, and structure extraction.
  - `check-links.py`: Relative markdown link and anchor slug validator.
  - `validate-docs.py`: Document structure, H1, and placeholder linter.
  - `detect-secrets.py`: Secret scanner with automatic redaction.
- Modular reference documentation under `skills/code-documentation/references/`:
  - `project-discovery.md`
  - `codebase-analysis.md`
  - `documentation-standards.md`
  - `readme-guidelines.md`
  - `documentation-validation.md`
  - `quality-checklist.md`
  - `architecture-documentation.md`
  - `api-documentation.md`
  - `database-documentation.md`
  - `mermaid-guidelines.md`
  - `documentation-updates.md`
- Markdown templates in `skills/code-documentation/assets/`:
  - `README.template.md`
  - `ARCHITECTURE.template.md`
  - `API.template.md`
  - `DATABASE.template.md`
- Sample fixtures:
  - `tests/fixtures/nodejs-typescript` (Express, TypeScript)
  - `tests/fixtures/python` (FastAPI, Pydantic)
- Automated unit test suite with 100% standard library `unittest` runner.
- Continuous integration workflow definition (`.github/workflows/validate.yml`).
