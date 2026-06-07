"""用户引导服务 / Onboarding service.

交互式教程 + 示例项目 + Prompt模板库 + 渐进式功能解锁。
参考规划文档中产品经理视角第16项。
"""

from datetime import datetime
from typing import Optional


ONBOARDING_STEPS = [
    {
        "id": "welcome",
        "title": "欢迎使用 OpenAgent",
        "title_en": "Welcome to OpenAgent",
        "description": "了解 OpenAgent 的核心理念：AI 驱动的全生命周期开发",
        "description_en": "Learn the core concept: AI-driven full lifecycle development",
        "type": "info",
        "order": 1,
    },
    {
        "id": "choose_mode",
        "title": "选择运行模式",
        "title_en": "Choose Running Mode",
        "description": "Localhost（本地 Docker）/ Cascade（编辑器内）/ Cloud（云端虚拟机）",
        "description_en": "Localhost (local Docker) / Cascade (in-editor) / Cloud (remote VM)",
        "type": "selection",
        "order": 2,
    },
    {
        "id": "connect_repo",
        "title": "连接代码仓库",
        "title_en": "Connect Repository",
        "description": "连接 GitHub / GitLab 仓库，Agent 将在沙箱中操作你的代码",
        "description_en": "Connect GitHub / GitLab repo, Agent operates your code in sandbox",
        "type": "action",
        "order": 3,
    },
    {
        "id": "configure_llm",
        "title": "配置 LLM 模型",
        "title_en": "Configure LLM Model",
        "description": "选择 GPT-4o / DeepSeek / Qwen / Claude / Ollama 并配置 API Key",
        "description_en": "Choose GPT-4o / DeepSeek / Qwen / Claude / Ollama and set API Key",
        "type": "config",
        "order": 4,
    },
    {
        "id": "first_session",
        "title": "创建第一个会话",
        "title_en": "Create First Session",
        "description": "尝试让 Agent 帮你完成一个简单任务，体验 ReAct 循环",
        "description_en": "Try Agent on a simple task, experience the ReAct loop",
        "type": "action",
        "order": 5,
    },
    {
        "id": "explore_deepwiki",
        "title": "探索 DeepWiki",
        "title_en": "Explore DeepWiki",
        "description": "索引你的仓库，查看自动生成的符号级文档",
        "description_en": "Index your repo and view auto-generated symbol-level docs",
        "type": "action",
        "order": 6,
    },
    {
        "id": "explore_codemap",
        "title": "探索 CodeMap",
        "title_en": "Explore CodeMap",
        "description": "可视化你的代码结构：依赖关系图 + 调用图 + 模块概览",
        "description_en": "Visualize code structure: dependency graph + call graph + module overview",
        "type": "action",
        "order": 7,
    },
]

SAMPLE_PROJECTS = [
    {
        "id": "hello-fastapi",
        "name": "Hello FastAPI",
        "description": "快速创建一个 FastAPI REST API 项目",
        "description_en": "Quickly create a FastAPI REST API project",
        "language": "python",
        "difficulty": "beginner",
        "estimated_time": "5 min",
        "prompt": "帮我创建一个 FastAPI 项目，包含用户注册和登录 API",
    },
    {
        "id": "react-todo",
        "name": "React Todo App",
        "description": "使用 React + TypeScript 构建待办事项应用",
        "description_en": "Build a todo app with React + TypeScript",
        "language": "typescript",
        "difficulty": "beginner",
        "estimated_time": "10 min",
        "prompt": "帮我创建一个 React Todo App，支持添加/删除/标记完成",
    },
    {
        "id": "fullstack-blog",
        "name": "全栈博客系统",
        "description": "Next.js + FastAPI + PostgreSQL 全栈博客",
        "description_en": "Full-stack blog with Next.js + FastAPI + PostgreSQL",
        "language": "fullstack",
        "difficulty": "intermediate",
        "estimated_time": "30 min",
        "prompt": "帮我创建一个博客系统，包含文章 CRUD、Markdown 渲染、分类标签",
    },
    {
        "id": "cli-tool",
        "name": "CLI 工具开发",
        "description": "使用 Python Click 构建命令行工具",
        "description_en": "Build a CLI tool with Python Click",
        "language": "python",
        "difficulty": "intermediate",
        "estimated_time": "15 min",
        "prompt": "帮我创建一个 CLI 工具，支持文件批量重命名和格式转换",
    },
]

PROMPT_TEMPLATES = [
    {
        "id": "bug-fix",
        "name": "修复 Bug",
        "name_en": "Fix Bug",
        "category": "debug",
        "template": "我在 {file} 文件中发现了一个 Bug：{description}。请帮我分析原因并修复。",
        "template_en": "I found a bug in {file}: {description}. Please analyze and fix it.",
        "variables": ["file", "description"],
    },
    {
        "id": "add-feature",
        "name": "添加功能",
        "name_en": "Add Feature",
        "category": "development",
        "template": "请帮我在 {module} 模块中添加 {feature} 功能，需要包含测试。",
        "template_en": "Please add {feature} to the {module} module, including tests.",
        "variables": ["module", "feature"],
    },
    {
        "id": "refactor",
        "name": "代码重构",
        "name_en": "Code Refactor",
        "category": "refactor",
        "template": "请重构 {file}，目标：{goal}。保持所有测试通过。",
        "template_en": "Please refactor {file}, goal: {goal}. Keep all tests passing.",
        "variables": ["file", "goal"],
    },
    {
        "id": "write-tests",
        "name": "编写测试",
        "name_en": "Write Tests",
        "category": "testing",
        "template": "请为 {module} 编写单元测试，覆盖核心逻辑和边界情况。",
        "template_en": "Write unit tests for {module}, covering core logic and edge cases.",
        "variables": ["module"],
    },
    {
        "id": "code-review",
        "name": "代码审查",
        "name_en": "Code Review",
        "category": "review",
        "template": "请审查最近的代码变更，检查：安全性、性能、代码风格、测试覆盖。",
        "template_en": "Review recent changes for: security, performance, style, test coverage.",
        "variables": [],
    },
    {
        "id": "api-design",
        "name": "API 设计",
        "name_en": "API Design",
        "category": "design",
        "template": "请为 {resource} 设计 RESTful API，包含 CRUD 端点、Pydantic Schema 和错误处理。",
        "template_en": "Design RESTful API for {resource} with CRUD endpoints, schemas and error handling.",
        "variables": ["resource"],
    },
]

ENVIRONMENT_PRESETS = [
    {
        "id": "python-fastapi",
        "name": "Python + FastAPI",
        "icon": "🐍",
        "stack": ["Python 3.12", "FastAPI", "PostgreSQL", "pytest"],
        "blueprint": {
            "initialize": "pip install fastapi uvicorn sqlalchemy alembic pytest",
            "maintenance": "pip install -r requirements.txt",
        },
    },
    {
        "id": "node-nextjs",
        "name": "Node.js + Next.js",
        "icon": "⚛️",
        "stack": ["Node.js 20", "Next.js 14", "TypeScript", "Jest"],
        "blueprint": {
            "initialize": "npm install",
            "maintenance": "npm install",
        },
    },
    {
        "id": "rust-actix",
        "name": "Rust + Actix",
        "icon": "🦀",
        "stack": ["Rust 1.78", "Actix-web", "SQLx", "cargo-test"],
        "blueprint": {
            "initialize": "cargo build",
            "maintenance": "cargo build",
        },
    },
    {
        "id": "go-gin",
        "name": "Go + Gin",
        "icon": "🐹",
        "stack": ["Go 1.22", "Gin", "GORM", "go test"],
        "blueprint": {
            "initialize": "go mod download",
            "maintenance": "go mod download",
        },
    },
    {
        "id": "java-spring",
        "name": "Java + Spring Boot",
        "icon": "☕",
        "stack": ["Java 21", "Spring Boot 3", "PostgreSQL", "JUnit 5"],
        "blueprint": {
            "initialize": "mvn install -DskipTests",
            "maintenance": "mvn install -DskipTests",
        },
    },
    {
        "id": "fullstack",
        "name": "全栈 (Next.js + FastAPI)",
        "icon": "🌐",
        "stack": ["Next.js 14", "FastAPI", "PostgreSQL", "Docker"],
        "blueprint": {
            "initialize": "npm install && pip install -r requirements.txt",
            "maintenance": "npm install && pip install -r requirements.txt",
        },
    },
]


class OnboardingService:
    """用户引导管理."""

    def __init__(self):
        self._user_progress: dict[str, dict] = {}

    def get_steps(self) -> list[dict]:
        return ONBOARDING_STEPS

    def get_user_progress(self, user_id: str) -> dict:
        if user_id not in self._user_progress:
            self._user_progress[user_id] = {
                "user_id": user_id,
                "completed_steps": [],
                "current_step": "welcome",
                "started_at": datetime.utcnow().isoformat(),
                "completed": False,
            }
        return self._user_progress[user_id]

    def complete_step(self, user_id: str, step_id: str) -> dict:
        progress = self.get_user_progress(user_id)
        if step_id not in progress["completed_steps"]:
            progress["completed_steps"].append(step_id)
        # advance to next step
        all_ids = [s["id"] for s in ONBOARDING_STEPS]
        idx = all_ids.index(step_id) if step_id in all_ids else -1
        if idx + 1 < len(all_ids):
            progress["current_step"] = all_ids[idx + 1]
        else:
            progress["completed"] = True
            progress["completed_at"] = datetime.utcnow().isoformat()
        return progress

    def skip_onboarding(self, user_id: str) -> dict:
        progress = self.get_user_progress(user_id)
        progress["completed"] = True
        progress["skipped"] = True
        return progress

    def get_sample_projects(self) -> list[dict]:
        return SAMPLE_PROJECTS

    def get_prompt_templates(self, category: Optional[str] = None) -> list[dict]:
        if category:
            return [t for t in PROMPT_TEMPLATES if t["category"] == category]
        return PROMPT_TEMPLATES

    def get_environment_presets(self) -> list[dict]:
        return ENVIRONMENT_PRESETS


onboarding_service = OnboardingService()
