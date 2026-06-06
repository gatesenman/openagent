# OpenAgent — AI 驱动的全生命周期软件开发平台

[English](#english) | [中文](#中文)

## 中文

### 概述

OpenAgent 是一个 AI 驱动的虚拟化软件开发平台，支持从规划、编码、测试、调试到部署的全生命周期管理。
系统核心是**零幻觉开发**：通过真实环境执行 + 精准代码索引 + 实时验证反馈的闭环实现。

### 核心特性

- **Agent 驱动开发** — 非传统 IDE 模式，Agent 主动规划并执行，用户通过对话监督审批
- **三种运行模式** — Localhost（本地）/ Cascade（编辑器内）/ Cloud（云端虚拟机）
- **零幻觉引擎** — 7 层能力栈保障每行代码都经过真实验证
- **DeepWiki** — 仓库级自动文档生成，符号级定义/用法/注释
- **CodeMap** — 代码结构可视化，流程图 + 层级展开 + 源码引用
- **行业标准兼容** — MCP / A2A / AG-UI / OpenAPI / OAuth 2.0 / AGENTS.md / OpenTelemetry
- **多模型支持** — Claude / GPT / DeepSeek / Qwen，智能路由自动选择
- **中英双语** — 默认中文界面，支持英文切换
- **跨平台** — 支持 Ubuntu 22.04 + Windows Server 2022

### 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js 14, React 18, TypeScript, Tailwind CSS, next-intl |
| 后端 | FastAPI, Python 3.12, SQLAlchemy, Alembic |
| 数据库 | PostgreSQL 16 + pgvector |
| Agent | ReAct Loop, LangChain, Tree-sitter |
| 虚拟环境 | Docker (Phase 1), KVM/QEMU (Phase 2) |
| 通信 | JSON-RPC 2.0, SSE, WebSocket |
| 协议 | MCP, A2A, AG-UI, OpenAPI 3.1 |

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/gaosichun888/openagent.git
cd openagent

# 启动后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 项目结构

```
openagent/
├── frontend/          # Next.js 前端
│   ├── src/
│   │   ├── app/       # App Router 页面
│   │   ├── components/# React 组件
│   │   ├── lib/       # 工具库
│   │   └── i18n/      # 国际化
│   └── package.json
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/       # REST API 路由
│   │   ├── core/      # 核心配置
│   │   ├── models/    # 数据模型
│   │   ├── services/  # 业务逻辑
│   │   └── agent/     # Agent 引擎
│   └── requirements.txt
└── docs/              # 设计文档
```

---

<a id="english"></a>
## English

### Overview

OpenAgent is an AI-driven virtualized software development platform supporting full lifecycle management from planning, coding, testing, debugging to deployment. The core is **zero-hallucination development**: achieved through real environment execution + precise code indexing + real-time validation feedback loop.

### Key Features

- **Agent-Driven Development** — Not a traditional IDE; Agent proactively plans and executes while users supervise via dialogue
- **Three Running Modes** — Localhost / Cascade (in-editor) / Cloud (remote VM)
- **Zero-Hallucination Engine** — 7-layer capability stack ensures every line of code is verified in real environment
- **DeepWiki** — Repository-level auto documentation with symbol-level definitions/usage/notes
- **CodeMap** — Code structure visualization with flow diagrams + hierarchical expansion + source references
- **Industry Standards** — MCP / A2A / AG-UI / OpenAPI / OAuth 2.0 / AGENTS.md / OpenTelemetry
- **Multi-Model Support** — Claude / GPT / DeepSeek / Qwen with intelligent routing
- **Bilingual** — Chinese default with English support
- **Cross-Platform** — Ubuntu 22.04 + Windows Server 2022

### License

MIT
