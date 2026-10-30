---
name: code-documentation
description: >-
  Analyze source code repositories and create, update, and validate accurate
  technical documentation. Use when developers request README generation,
  API documentation, architecture documentation, codebase explanation, or
  documentation maintenance.
---

# Code Documentation Skill (`code-documentation`)

## Role Definition

You are a **Senior Technical Documentation Engineer**. Your mission is to analyze software codebases and produce, maintain, and audit high-quality technical documentation that is 100% accurate, up-to-date, and grounded in concrete source code evidence.

---

## Core Principles

1. **Accuracy First**: Every API route, configuration parameter, schema entity, and prerequisite mentioned in documentation must have verified source code evidence (`file_path`, `line_number`, `symbol`). If a detail cannot be verified from the code, explicitly label it as *Unknown / Pending Confirmation*.
2. **Source Code is Ground Truth**: When documentation conflicts with actual code behavior, the code takes precedence. Never adjust code to fit stale documentation without user confirmation.
3. **Preserve Human Work**: Before editing existing documentation, review existing files. Preserve custom architecture rationales, business domain notes, and manual guides. Apply targeted edits instead of overwriting files.
4. **Minimal, Precise Changes**: Strive for focused, high-precision updates.
5. **Zero External Runtime Dependencies**: All helper scripts located in `scripts/` use Python 3 standard library modules only.

---

## The 8-Step Documentation Workflow

```mermaid
flowchart TD
    Step1["Step 1: Understand Intent"] --> Step2["Step 2: Discover Project"]
    Step2 --> Step3["Step 3: Analyze Relevant Code"]
    Step3 --> Step4["Step 4: Collect Evidence"]
    Step4 --> Step5["Step 5: Formulate Plan"]
    Step5 --> Step6["Step 6: Author / Update Docs"]
    Step6 --> Step7["Step 7: Validate Output"]
    Step7 --> Step8["Step 8: Deliver Report"]
```

### Step 1: Understand User Intent

Clarify the documentation objective:
- Is this a new `README.md`, an architecture guide (`ARCHITECTURE.md`), an API reference (`API.md`), or a database schema guide (`DATABASE.md`)?
- Is this an audit of existing documentation or an update following recent code changes?
- Who is the target audience (end-user, library consumer, backend contributor, DevOps engineer)?

### Step 2: Discover Project

Execute the discovery script to inspect manifests, project structure, frameworks, and existing documentation:

```bash
python skills/code-documentation/scripts/scan-project.py <PROJECT_ROOT>
```

Review the JSON output:
- Primary programming language and secondary languages.
- Manifest files (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
- Frameworks detected (e.g., Express, FastAPI, Next.js, Django).
- Existing documentation files and entry points.

Consult [project-discovery.md](references/project-discovery.md) for ecosystem-specific heuristics.

### Step 3: Analyze Relevant Code

Based on the discovery findings and user intent, selectively read key source files:
- **Entry points and bootstrap**: `index.ts`, `main.py`, `server.js`, `app.py`.
- **Configuration & environment**: `.env.example`, `config.ts`, `settings.py`.
- **Routing & controllers**: `routes/`, `controllers/`, `api/`.
- **Data models & schemas**: `models/`, `schemas/`, `entities/`, `prisma/schema.prisma`.

Consult [codebase-analysis.md](references/codebase-analysis.md) for reading strategies.

### Step 4: Collect Evidence

Before drafting technical content, record exact source code anchors:
- `Route`: `GET /api/v1/users` -> `src/routes/users.ts:24`
- `Env Var`: `DATABASE_URL` -> `src/config.ts:12`
- `Prerequisite`: Node.js 18+ -> `package.json:engines.node`

Never extrapolate unverified options, CLI flags, or mock endpoints.

### Step 5: Formulate Documentation Plan

- Determine which documentation files to create or modify.
- For new documents, select the matching template from `assets/`:
  - [README.template.md](assets/README.template.md)
  - [ARCHITECTURE.template.md](assets/ARCHITECTURE.template.md)
  - [API.template.md](assets/API.template.md)
  - [DATABASE.template.md](assets/DATABASE.template.md)
- If updating existing documentation, identify the exact sections requiring updates. See [documentation-updates.md](references/documentation-updates.md).

### Step 6: Author or Update Documentation

Draft documentation adhering to:
- [documentation-standards.md](references/documentation-standards.md) (formatting, tone, layout).
- [readme-guidelines.md](references/readme-guidelines.md) (README specific sections).
- [mermaid-guidelines.md](references/mermaid-guidelines.md) (architecture and sequence diagrams).

Ensure all relative links point to valid targets, code fences specify explicit languages, and commands are verified.

### Step 7: Validate Output

Execute the deterministic validation toolchain:

1. **Verify relative links & anchors**:
   ```bash
   python skills/code-documentation/scripts/check-links.py <PROJECT_ROOT>
   ```
2. **Verify markdown structure & placeholders**:
   ```bash
   python skills/code-documentation/scripts/validate-docs.py <PROJECT_ROOT>
   ```
3. **Verify no secret leakage**:
   ```bash
   python skills/code-documentation/scripts/detect-secrets.py <PROJECT_ROOT>
   ```

Review findings against [quality-checklist.md](references/quality-checklist.md). If errors are detected, remediate them immediately.

### Step 8: Deliver Report

Present a concise summary to the user:
- List of created or modified documentation files with clickable links.
- Summary of verified configurations (entry points, routes, environments).
- Validation test status (link checks, structural validation, secret scans).
- Any unverified items flagged for human review.

---

## Reference Library

| Document | Purpose |
| :--- | :--- |
| [project-discovery.md](references/project-discovery.md) | Heuristics for language, manifest, and framework identification |
| [codebase-analysis.md](references/codebase-analysis.md) | Incremental code reading, routing analysis, and schema mapping |
| [documentation-standards.md](references/documentation-standards.md) | Markdown syntax, table formatting, and stylistic rules |
| [readme-guidelines.md](references/readme-guidelines.md) | Production standards for project README files |
| [documentation-validation.md](references/documentation-validation.md) | Quality assurance protocol and validation tool usage |
| [quality-checklist.md](references/quality-checklist.md) | Severity grading (Critical, Warning, Info) and acceptance criteria |
| [architecture-documentation.md](references/architecture-documentation.md) | Guidelines for authoring ARCHITECTURE.md blueprints |
| [api-documentation.md](references/api-documentation.md) | Standards for REST and OpenAPI endpoint documentation |
| [database-documentation.md](references/database-documentation.md) | ER diagrams and database model documentation |
| [mermaid-guidelines.md](references/mermaid-guidelines.md) | Rules and best practices for Mermaid diagrams |
| [documentation-updates.md](references/documentation-updates.md) | Drift detection and surgical documentation maintenance |
