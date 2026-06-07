# 贡献指南 / Contributing Guide

感谢你对 OpenAgent 的关注！以下是参与贡献的指南。

## 项目结构

```
openagent/
├── backend/         # Python FastAPI 后端
│   ├── app/
│   │   ├── api/     # REST API 路由 (30+ 模块)
│   │   ├── agent/   # Agent 引擎 (ReAct + 工具链)
│   │   ├── sandbox/ # 沙箱虚拟化层
│   │   ├── services/# 业务服务层
│   │   ├── protocols/# 协议层 (MCP/A2A/AG-UI)
│   │   ├── models/  # 数据模型
│   │   ├── schemas/ # Pydantic Schema
│   │   └── core/    # 核心配置
│   └── tests/       # 测试套件
├── frontend/        # Next.js 14 前端
│   └── src/
│       ├── app/     # App Router 页面 (20+ 页面)
│       ├── components/ # React 组件
│       ├── lib/     # API 客户端
│       └── messages/# i18n 翻译 (zh/en)
├── cli/             # 命令行工具
├── desktop/         # Tauri 桌面客户端
└── docs/            # 文档和截图
```

## 开发环境

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 测试

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

## 代码规范

### Python (后端)

- 使用 Python 3.12+
- 类型注解 (Type Hints) 必须
- Docstring 使用中英双语
- 命名: snake_case (函数/变量), PascalCase (类)

### TypeScript (前端)

- 使用 TypeScript strict mode
- 所有组件使用 "use client" 标注
- i18n: 所有用户可见文本通过 useTranslations 获取
- 样式: Tailwind CSS + CSS 变量

### Git 提交

- 使用语义化提交: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- 每个提交应该是独立可用的
- 提交信息可以使用中文或英文

## 添加新功能

### 添加新 API 端点

1. 在 `backend/app/services/` 创建服务
2. 在 `backend/app/api/` 创建路由
3. 在 `backend/app/main.py` 注册路由
4. 在 `backend/tests/test_api.py` 添加测试
5. 运行测试确保通过

### 添加新前端页面

1. 在 `frontend/src/app/{name}/page.tsx` 创建页面
2. 使用 `useTranslations("pageName")` 进行 i18n
3. 在 `frontend/src/messages/zh.json` 添加中文翻译
4. 在 `frontend/src/messages/en.json` 添加英文翻译
5. 在 `frontend/src/components/layout/Sidebar.tsx` 添加导航项

## 协议扩展

OpenAgent 支持多种 Agent 协议。添加新协议时：

1. 在 `backend/app/protocols/` 实现协议
2. 在 `backend/app/main.py` 注册
3. 更新 `/.well-known/agent.json` 声明
4. 更新 `AGENTS.md` 文档

## 分支策略

- `main` — 稳定版本
- `scaffold` — 开发分支
- `feature/*` — 功能分支

## 许可证

MIT License
