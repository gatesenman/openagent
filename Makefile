.PHONY: help dev build test lint format clean

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==================== 开发 ====================

dev: ## 启动开发环境（Docker Compose）
	docker-compose up -d

dev-backend: ## 仅启动后端
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## 仅启动前端
	cd frontend && npm run dev

stop: ## 停止所有服务
	docker-compose down

# ==================== 构建 ====================

build: ## 构建所有镜像
	docker-compose build

build-backend: ## 构建后端镜像
	docker build -t openagent-backend ./backend

build-frontend: ## 构建前端镜像
	docker build -t openagent-frontend ./frontend

# ==================== 代码质量 ====================

lint: lint-backend lint-frontend ## 检查所有代码

lint-backend: ## 检查后端代码
	cd backend && python -m ruff check .

lint-frontend: ## 检查前端代码
	cd frontend && npm run lint

format: ## 格式化代码
	cd backend && python -m ruff format .

typecheck: ## 类型检查
	cd backend && python -m mypy app/ --ignore-missing-imports
	cd frontend && npx tsc --noEmit

# ==================== 测试 ====================

test: test-backend test-frontend ## 运行所有测试

test-backend: ## 运行后端测试
	cd backend && python -m pytest tests/ -v

test-frontend: ## 运行前端测试
	cd frontend && npm test

# ==================== 数据库 ====================

db-migrate: ## 运行数据库迁移
	cd backend && alembic upgrade head

db-reset: ## 重置数据库
	cd backend && alembic downgrade base && alembic upgrade head

# ==================== 清理 ====================

clean: ## 清理生成文件
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

# ==================== DeepWiki ====================

index-repo: ## 索引仓库代码（DeepWiki）
	curl -X POST http://localhost:8000/api/deepwiki/index \
		-H "Content-Type: application/json" \
		-d '{"repo_path": "."}'

# ==================== CodeMap ====================

analyze: ## 分析代码结构（CodeMap）
	curl -X POST http://localhost:8000/api/codemaps/analyze \
		-H "Content-Type: application/json" \
		-d '{"repo_path": "."}'
