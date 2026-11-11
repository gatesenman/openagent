# OpenAgent

**English** | [简体中文](./README.zh-CN.md)

AI-driven, full-lifecycle software development platform: a FastAPI backend with an agent engine and sandboxed execution, plus a Next.js web console (Chinese/English UI, dark theme). Agents run inside a sandbox (Docker by default, or local).

> Status: active development (`scaffold` branch). Many console pages currently render built-in sample data rather than live backend data; see [Known issues](#known-issues).

## Features

- **Agent engine** (`backend/app/agent`): ReAct loop, task planner, multi-agent orchestration, model router, context manager, self-healing, anti-hallucination validators, tool guard, computer use.
- **Agent tools**: file operations, git operations, code search, shell execution.
- **Sandboxes** (`backend/app/sandbox`): Docker sandbox and local sandbox behind a sandbox manager.
- **Protocols** (`backend/app/protocols`): JSON-RPC 2.0, MCP, AG-UI, A2A.
- **REST API** (FastAPI, 37 routers): sessions, agents, tools, DeepWiki, CodeMap, knowledge, playbooks, auth, events (SSE), analytics, automations, git, MCP marketplace, devbox, secrets, blueprints, skills, API keys, audit, repos, memory, PR review, notifications, worklog, orgs, billing, batch sessions, CI/CD, snapshots, schedules, SSO, onboarding, security, Codex security (SAST / SCA / secret detection / license / IaC / SBOM), evaluation, computer use.
- **Web console** (`frontend`): Next.js 14 + TailwindCSS + next-intl (Chinese by default, English available).
- **CLI** (`cli/openagent_cli.py`): `init`, `start`, `session new|list|logs`, `handoff`, `status`, `deploy`, `test`, `review`, `config`.
- **Desktop shell** (`desktop`): Tauri 2 project (not verified, see Known issues).

## Screenshots

All screenshots were captured from a local run (`uvicorn` backend + `next dev` frontend) with headless Chromium at 1440×900.

| Home | Sessions |
| --- | --- |
| ![Home](docs/screenshots/home.png) | ![Sessions](docs/screenshots/sessions.png) |
| **Ask** | **DeepWiki** |
| ![Ask](docs/screenshots/ask.png) | ![DeepWiki](docs/screenshots/deepwiki.png) |
| **CodeMap** | **Knowledge** |
| ![CodeMap](docs/screenshots/codemap.png) | ![Knowledge](docs/screenshots/knowledge.png) |
| **Review** | **Security center** |
| ![Review](docs/screenshots/review.png) | ![Security](docs/screenshots/security.png) |
| **Automations** | **Playbooks** |
| ![Automations](docs/screenshots/automations.png) | ![Playbooks](docs/screenshots/playbooks.png) |
| **Analytics** | **CI/CD** |
| ![Analytics](docs/screenshots/analytics.png) | ![CI/CD](docs/screenshots/cicd.png) |
| **Schedules** | **Snapshots** |
| ![Schedules](docs/screenshots/schedules.png) | ![Snapshots](docs/screenshots/snapshots.png) |
| **Onboarding** | **Settings** |
| ![Onboarding](docs/screenshots/onboarding.png) | ![Settings](docs/screenshots/settings.png) |
| **Login** | **API docs (Swagger, `:8000/docs`)** |
| ![Login](docs/screenshots/login.png) | ![API docs](docs/screenshots/api-docs.png) |

## Tech stack

| Layer | Stack |
| --- | --- |
| Backend | Python 3.12, FastAPI 0.115, SQLAlchemy 2, Alembic, Pydantic Settings, sse-starlette, OpenAI SDK, tiktoken, tree-sitter |
| Database | SQLite by default (`sqlite:///./openagent.db`); PostgreSQL 16 in Docker Compose |
| Frontend | Next.js 14, React 18, TypeScript, TailwindCSS 3, next-intl, next-themes, lucide-react |
| Desktop | Tauri 2 |
| Tests / CI | pytest (153 tests), ruff, GitHub Actions |

## Quick start

### Option A: Docker Compose (Postgres + backend + frontend)

```bash
cp .env.example .env   # fill in your LLM key
make dev               # = docker-compose up -d
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (Swagger UI at `/docs`, health check at `/health`)

### Option B: run locally without Docker

Backend (uses SQLite by default; tables are created on startup):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000   # = make dev-backend
```

Frontend:

```bash
cd frontend
npm install
npm run dev            # = make dev-frontend, http://localhost:3000
```

### CLI

```bash
cd cli && pip install -e .
openagent --help
```

### Common commands

```bash
make test-backend      # cd backend && python -m pytest tests/ -v
make lint-backend      # ruff check
make format            # ruff format
make typecheck         # mypy + tsc --noEmit
make db-migrate        # alembic upgrade head
make help              # list all targets
```

## Project structure

```text
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── agent/        # agent engine (ReAct, planner, multi-agent, tools/)
│   │   ├── api/          # REST routers (37 modules)
│   │   ├── core/         # config, database, auth, event hub
│   │   ├── models/       # SQLAlchemy models
│   │   ├── protocols/    # JSON-RPC, MCP, AG-UI, A2A
│   │   ├── sandbox/      # docker / local sandboxes
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # business services (deepwiki, codemap, knowledge, ...)
│   │   └── main.py
│   ├── alembic/          # migrations
│   └── tests/            # pytest
├── frontend/             # Next.js 14 web console
│   └── src/{app,components,lib,messages}
├── desktop/              # Tauri 2 desktop shell
├── cli/                  # openagent CLI
├── docs/screenshots/
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Configuration

Copy `.env.example` to `.env`. Main variables:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Database URL (backend default: `sqlite:///./openagent.db`) |
| `LLM_PROVIDER`, `LLM_MODEL` | `openai` / `deepseek` / `qwen` / `anthropic` / `ollama`, and model name |
| `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `QWEN_API_KEY`, `ANTHROPIC_API_KEY`, `OLLAMA_BASE_URL` | Provider credentials / endpoints |
| `SANDBOX_TYPE` | `docker` or `local` |
| `SANDBOX_DOCKER_IMAGE`, `SANDBOX_CPU_LIMIT`, `SANDBOX_MEMORY_LIMIT`, `SANDBOX_TIMEOUT` | Sandbox limits |
| `MCP_ENABLED`, `AGUI_ENABLED` | Protocol switches |
| `NEXT_PUBLIC_API_URL` | Backend URL used by the frontend (default `http://localhost:8000`) |
| `NEXT_PUBLIC_DEFAULT_LOCALE` | UI default locale (`zh`) |
| `SECRET_KEY`, `CORS_ORIGINS` | Security settings — change `SECRET_KEY` in production |

Important: the backend (`backend/app/core/config.py`, `services/llm_service.py`) actually reads **`LLM_API_KEY`** and `LLM_BASE_URL`; the per-provider keys in `.env.example` (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, …) are not read by the backend code. Set `LLM_API_KEY` in `.env`. Without it the LLM service runs in mock mode (`[Mock模式] 请配置 LLM_API_KEY …`).

## Known issues

- Many console pages (Sessions list, DeepWiki, CodeMap, Knowledge, Review, Security, Analytics, CI/CD, …) render hard-coded sample data in the frontend and do not yet call the backend API. The numbers in the screenshots are that sample data.
- Clicking a sample session in **Sessions** does not open a detail view.
- `desktop/package.json` scripts call `next dev` / `next build && next export`, but `desktop/src` contains a single `App.tsx` and there is no Next config; the desktop build was not verified.
- Next.js prints a deprecation warning: `next-intl` config in `src/i18n.ts` should move to `i18n/request.ts`.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) and [AGENTS.md](./AGENTS.md) (coding conventions: ruff, async-first, next-intl, components under `src/components/`).

## License

No license file is included in this repository yet.
