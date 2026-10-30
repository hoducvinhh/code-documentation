# Project Roadmap

This document outlines the planned trajectory for `code-documentation-skill`.

---

## Phase 1: MVP Foundation (Current Phase)

- [x] Standard Agent Skills directory structure.
- [x] Core `SKILL.md` specification with 8-step workflow.
- [x] 4 Zero-dependency Python CLI helper scripts (`scan-project.py`, `check-links.py`, `validate-docs.py`, `detect-secrets.py`).
- [x] Modular technical references in `references/`.
- [x] Production-ready templates in `assets/`.
- [x] Fixture codebases (`nodejs-typescript`, `python`).
- [x] Unit test suite covering all helper scripts.
- [x] Self-validation and CI workflow configuration.

---

## Phase 2: Advanced Documentation Generation

- [ ] AST parsing helpers for popular languages (Python `ast`, TypeScript/JavaScript AST via node, Go `go/parser`).
- [ ] Automated OpenAPI / Swagger schema generator from route definitions.
- [ ] Database schema extraction from Prisma, TypeORM, SQLAlchemy, Alembic, and Django models.
- [ ] Automatic Mermaid diagram generation (Sequence diagrams, Entity-Relationship diagrams, Flowcharts).
- [ ] Support for Monorepo setups (Turborepo, Nx, Lerna, Cargo Workspaces, Go Workspaces).

---

## Phase 3: Documentation Maintenance & Drift Detection

- [ ] Git diff analyzer to identify modified endpoints, schemas, or config files since last doc update.
- [ ] Automated doc drift scoring tool (`drift-score.py`).
- [ ] Targeted surgical doc patch generation (micro-updates without rewriting files).
- [ ] PR comment bot integration for CI-based documentation checks.

---

## Phase 4: Ecosystem & Multi-Agent Compatibility

- [ ] Community verification across major AI platforms: Cursor, Claude Code, Antigravity, GitHub Copilot Workspace, Codex.
- [ ] Expansion of language fixtures: Rust, Go, Java/Spring Boot, C#/.NET.
- [ ] Integration with static site generators (VitePress, Docusaurus, MkDocs, Starlight).
