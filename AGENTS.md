# OpenAgent - Agent 配置

## 项目说明

OpenAgent 是 AI 驱动的全生命周期软件开发平台。
所有 Agent 操作在沙箱虚拟环境中执行。

## 技术栈

- **后端**: Python 3.12 + FastAPI + SQLAlchemy + PostgreSQL
- **前端**: Next.js 14 + TypeScript + TailwindCSS + next-intl
- **沙箱**: Docker 容器 (Phase 1) / KVM 虚拟机 (Phase 2)
- **协议**: JSON-RPC 2.0 + MCP + AG-UI + SSE

## 开发规范

### 后端
- 使用 ruff 进行代码检查和格式化
- 中文 docstring 和注释
- 异步优先 (async/await)
- 类型注解 (Python 3.12+ 语法)

### 前端
- 使用 next-intl 做中英双语，默认中文
- TailwindCSS 暗色主题
- 组件放在 src/components/ 对应子目录下
- API 调用使用 src/lib/api.ts

### Git 规范
- 提交信息使用中文或英文
- 不在提交信息中包含 bot/agent 自动化关键词
- 功能分支: feature/xxx
- 修复分支: fix/xxx

## 运行命令

```bash
# 启动全部服务
docker-compose up -d

# 仅启动后端
cd backend && uvicorn app.main:app --reload --port 8000

# 仅启动前端
cd frontend && npm run dev

# 代码检查
cd backend && ruff check .
cd frontend && npm run lint
```
