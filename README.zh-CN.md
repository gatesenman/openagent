# OpenAgent

[English](./README.md) | **简体中文**

AI 驱动的全生命周期软件开发平台：FastAPI 后端（Agent 引擎 + 沙箱执行）+ Next.js Web 控制台（中英双语、暗色主题）。所有 Agent 操作在沙箱中执行（默认 Docker，也可 local）。

> 状态：开发中（`scaffold` 分支）。控制台不少页面目前展示的是前端内置的示例数据，尚未接入后端，详见[已知问题](#已知问题)。

## 功能

- **Agent 引擎**（`backend/app/agent`）：ReAct 循环、任务规划、多 Agent 编排、模型路由、上下文管理、自愈、防幻觉校验、工具守卫、Computer Use。
- **Agent 工具**：文件操作、Git 操作、代码搜索、Shell 执行。
- **沙箱**（`backend/app/sandbox`）：Docker 沙箱、本地沙箱，由沙箱管理器统一调度。
- **协议**（`backend/app/protocols`）：JSON-RPC 2.0、MCP、AG-UI、A2A。
- **REST API**（FastAPI，37 个路由模块）：会话、Agent、工具、DeepWiki、CodeMap、知识库、Playbook、认证、事件流（SSE）、分析、自动化、Git、MCP 市场、DevBox、密钥、蓝图、技能、API Key、审计、仓库、记忆、PR 审查、通知、工作日志、组织、计费、批量会话、CI/CD、快照、调度、SSO、新手引导、安全、Codex 安全（SAST / SCA / 密钥检测 / 许可证 / IaC / SBOM）、评测、Computer Use。
- **Web 控制台**（`frontend`）：Next.js 14 + TailwindCSS + next-intl（默认中文，可切英文）。
- **命令行**（`cli/openagent_cli.py`）：`init`、`start`、`session new|list|logs`、`handoff`、`status`、`deploy`、`test`、`review`、`config`。
- **桌面端**（`desktop`）：Tauri 2 工程（未验证，见已知问题）。

## 截图

以下截图均为本地实际运行（`uvicorn` 后端 + `next dev` 前端）后用无头 Chromium 以 1440×900 截取。

| 首页 | 会话 |
| --- | --- |
| ![首页](docs/screenshots/home.png) | ![会话](docs/screenshots/sessions.png) |
| **Ask** | **DeepWiki** |
| ![Ask](docs/screenshots/ask.png) | ![DeepWiki](docs/screenshots/deepwiki.png) |
| **CodeMap** | **知识库** |
| ![CodeMap](docs/screenshots/codemap.png) | ![知识库](docs/screenshots/knowledge.png) |
| **Review** | **安全中心** |
| ![Review](docs/screenshots/review.png) | ![安全中心](docs/screenshots/security.png) |
| **自动化** | **Playbooks** |
| ![自动化](docs/screenshots/automations.png) | ![Playbooks](docs/screenshots/playbooks.png) |
| **分析** | **CI/CD** |
| ![分析](docs/screenshots/analytics.png) | ![CI/CD](docs/screenshots/cicd.png) |
| **调度管理** | **环境快照** |
| ![调度](docs/screenshots/schedules.png) | ![快照](docs/screenshots/snapshots.png) |
| **新手引导** | **设置** |
| ![新手引导](docs/screenshots/onboarding.png) | ![设置](docs/screenshots/settings.png) |
| **登录** | **API 文档（Swagger，`:8000/docs`）** |
| ![登录](docs/screenshots/login.png) | ![API 文档](docs/screenshots/api-docs.png) |

## 技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | Python 3.12、FastAPI 0.115、SQLAlchemy 2、Alembic、Pydantic Settings、sse-starlette、OpenAI SDK、tiktoken、tree-sitter |
| 数据库 | 默认 SQLite（`sqlite:///./openagent.db`）；Docker Compose 中为 PostgreSQL 16 |
| 前端 | Next.js 14、React 18、TypeScript、TailwindCSS 3、next-intl、next-themes、lucide-react |
| 桌面 | Tauri 2 |
| 测试 / CI | pytest（153 个用例）、ruff、GitHub Actions |

## 快速开始

### 方式 A：Docker Compose（Postgres + 后端 + 前端）

```bash
cp .env.example .env   # 填入 LLM Key
make dev               # 即 docker-compose up -d
```

- 前端：http://localhost:3000
- 后端：http://localhost:8000（Swagger 在 `/docs`，健康检查 `/health`）

### 方式 B：本地运行（不用 Docker）

后端（默认 SQLite，启动时自动建表）：

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000   # 即 make dev-backend
```

前端：

```bash
cd frontend
npm install
npm run dev            # 即 make dev-frontend，http://localhost:3000
```

### 命令行

```bash
cd cli && pip install -e .
openagent --help
```

### 常用命令

```bash
make test-backend      # cd backend && python -m pytest tests/ -v
make lint-backend      # ruff check
make format            # ruff format
make typecheck         # mypy + tsc --noEmit
make db-migrate        # alembic upgrade head
make help              # 列出所有目标
```

## 项目结构

```text
.
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── agent/        # Agent 引擎（ReAct、规划、多 Agent、tools/）
│   │   ├── api/          # REST 路由（37 个模块）
│   │   ├── core/         # 配置、数据库、认证、事件中心
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── protocols/    # JSON-RPC、MCP、AG-UI、A2A
│   │   ├── sandbox/      # docker / local 沙箱
│   │   ├── schemas/      # Pydantic 模型
│   │   ├── services/     # 业务服务（deepwiki、codemap、knowledge…）
│   │   └── main.py
│   ├── alembic/          # 数据库迁移
│   └── tests/            # pytest
├── frontend/             # Next.js 14 Web 控制台
│   └── src/{app,components,lib,messages}
├── desktop/              # Tauri 2 桌面壳
├── cli/                  # openagent 命令行
├── docs/screenshots/
├── docker-compose.yml
├── Makefile
└── .env.example
```

## 配置

复制 `.env.example` 为 `.env`。主要变量：

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | 数据库地址（后端默认 `sqlite:///./openagent.db`） |
| `LLM_PROVIDER`、`LLM_MODEL` | `openai` / `deepseek` / `qwen` / `anthropic` / `ollama` 及模型名 |
| `OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`QWEN_API_KEY`、`ANTHROPIC_API_KEY`、`OLLAMA_BASE_URL` | 各模型服务的密钥 / 地址 |
| `SANDBOX_TYPE` | `docker` 或 `local` |
| `SANDBOX_DOCKER_IMAGE`、`SANDBOX_CPU_LIMIT`、`SANDBOX_MEMORY_LIMIT`、`SANDBOX_TIMEOUT` | 沙箱资源限制 |
| `MCP_ENABLED`、`AGUI_ENABLED` | 协议开关 |
| `NEXT_PUBLIC_API_URL` | 前端访问的后端地址（默认 `http://localhost:8000`） |
| `NEXT_PUBLIC_DEFAULT_LOCALE` | 界面默认语言（`zh`） |
| `SECRET_KEY`、`CORS_ORIGINS` | 安全配置，生产环境务必修改 `SECRET_KEY` |

重要：后端（`backend/app/core/config.py`、`services/llm_service.py`）实际读取的是 **`LLM_API_KEY`** 和 `LLM_BASE_URL`；`.env.example` 里按厂商区分的 `OPENAI_API_KEY`、`DEEPSEEK_API_KEY` 等后端代码并不读取。请在 `.env` 中设置 `LLM_API_KEY`，否则 LLM 服务以 Mock 模式运行（返回「[Mock模式] 请配置 LLM_API_KEY …」）。

## 已知问题

- 控制台很多页面（会话列表、DeepWiki、CodeMap、知识库、Review、安全中心、分析、CI/CD 等）展示的是前端写死的示例数据，尚未调用后端 API；截图中的数字即为示例数据。
- 在「会话」中点击示例会话不会打开详情。
- `desktop/package.json` 的脚本是 `next dev` / `next build && next export`，但 `desktop/src` 只有一个 `App.tsx`，也没有 Next 配置；桌面端构建未验证。
- Next.js 启动时提示 `next-intl` 的 `src/i18n.ts` 配置方式已弃用，应迁移到 `i18n/request.ts`。

## 参与贡献

请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md) 和 [AGENTS.md](./AGENTS.md)（规范：ruff、异步优先、next-intl、组件放在 `src/components/`）。

## 许可证

仓库暂未包含许可证文件。
