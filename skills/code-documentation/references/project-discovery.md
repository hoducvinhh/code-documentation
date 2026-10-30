# Project Discovery & Stack Identification Guide

## Overview

Project discovery is the initial phase of any documentation engagement. Before writing or updating any document, the agent must systematically analyze the project hierarchy, dependency manifests, configuration files, and directory layouts to establish an accurate technical baseline.

---

## 1. Manifest Heuristics

The presence of specific manifest files reveals the ecosystem, package manager, and build tools:

| Manifest File | Ecosystem | Primary Package Manager | Default Build / Run Commands |
| :--- | :--- | :--- | :--- |
| `package.json` | Node.js / TypeScript | `npm`, `yarn`, `pnpm`, `bun` | `npm install`, `npm run build`, `npm start` |
| `pyproject.toml` | Python | `pip`, `poetry`, `uv`, `pdm` | `poetry install`, `pip install -e .` |
| `requirements.txt` | Python | `pip` | `pip install -r requirements.txt` |
| `Cargo.toml` | Rust | `cargo` | `cargo build`, `cargo run`, `cargo test` |
| `go.mod` | Go | `go` | `go build`, `go run .`, `go test ./...` |
| `pom.xml` | Java | `mvn` | `mvn clean install`, `mvn spring-boot:run` |
| `build.gradle` / `.kts` | Java / Kotlin | `gradle` | `./gradlew build`, `./gradlew test` |
| `composer.json` | PHP | `composer` | `composer install`, `composer run` |
| `Gemfile` | Ruby | `bundler` | `bundle install`, `bundle exec rails s` |
| `mix.exs` | Elixir | `mix` | `mix deps.get`, `mix phx.server` |
| `*.csproj`, `*.sln` | .NET / C# | `dotnet` | `dotnet restore`, `dotnet build`, `dotnet run` |

---

## 2. Framework Detection Rules

Inspect dependencies inside the manifest to classify the application framework:

### Node.js / TypeScript
- **Backend APIs**:
  - `express`: Express.js minimal HTTP server. Look for `express()`, `app.use()`, `app.listen()`.
  - `@nestjs/core`: NestJS modular framework. Look for `@Module()`, `@Controller()`, `@Injectable()`.
  - `fastify`: Fastify high-performance server. Look for `fastify()`, `fastify.register()`.
  - `koa`: Koa middleware framework. Look for `new Koa()`.
- **Full-stack & Frontend**:
  - `next`: Next.js React framework. Look for `app/` (App Router) or `pages/` (Pages Router).
  - `nuxt`: Nuxt.js Vue framework.
  - `svelte` / `@sveltejs/kit`: SvelteKit.
  - `react`: React SPA (often with Vite, Webpack, or CRA).

### Python
- `fastapi`: FastAPI modern async API. Look for `FastAPI()`, `@app.get()`, Pydantic models.
- `django`: Django enterprise framework. Look for `manage.py`, `settings.py`, `urls.py`.
- `flask`: Flask microframework. Look for `Flask(__name__)`, `@app.route()`.
- `tornado`: Tornado async networking.

---

## 3. Directory Layout Conventions

Modern codebases follow standard directory layouts that signal architectural intent:

```text
my-project/
├── src/ or app/              # Core application source code
│   ├── api/ or routes/       # Endpoint declarations, controllers
│   ├── services/             # Core business logic
│   ├── models/ or entities/  # Data schemas, database entities
│   ├── middleware/           # HTTP filters, auth interceptors
│   └── utils/ or common/     # Shared helper utilities
├── tests/ or __tests__/      # Automated test suites
├── config/ or .env.example   # Configuration and environment examples
├── docs/                     # Additional architectural or user documentation
├── public/ or assets/        # Static assets
└── scripts/                  # DevOps, deployment, or database migration scripts
```

---

## 4. Entry Point Identification

Always locate the executable entry point to trace program bootup:
- **Node.js**: Check `"main"` and `"scripts.start"` in `package.json`, then check `src/index.ts`, `src/main.ts`, `src/server.ts`, `server.js`.
- **Python**: Look for `main.py`, `app.py`, `wsgi.py`, `asgi.py`, or `[project.scripts]` in `pyproject.toml`.
- **Go**: Look for `main.go` or `cmd/<service>/main.go`.
- **Rust**: Look for `src/main.rs` (for binaries) or `src/lib.rs` (for libraries).

---

## 5. Automated Discovery with Helper Scripts

Run the bundled discovery tool:

```bash
python skills/code-documentation/scripts/scan-project.py . --format json
```

This outputs structured information including:
- Verified manifests and parsed dependencies.
- Language distribution metrics.
- Detected frameworks and entry points.
- Pre-existing documentation inventory.
