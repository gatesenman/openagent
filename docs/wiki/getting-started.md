# Getting Started

## Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (for sandbox mode)
- PostgreSQL 16 (or use Docker Compose)

## Installation

### Option 1: Desktop App (Recommended)

Download from [GitHub Releases](https://github.com/gaosichun888/openagent/releases):

- **Windows**: `OpenAgent_0.1.0_x64-setup.exe`
- **macOS**: `OpenAgent_0.1.0_x64.dmg`
- **Linux**: `openagent_0.1.0_amd64.deb` or `.AppImage`

### Option 2: Docker Compose

```bash
git clone https://github.com/gaosichun888/openagent.git
cd openagent
cp .env.example .env
# Edit .env: set DATABASE_URL, LLM_API_KEY, etc.
docker-compose up -d
```

### Option 3: Manual Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///openagent.db` |
| `LLM_API_KEY` | LLM provider API key | (required) |
| `LLM_MODEL` | Default model | `gpt-4o` |
| `SANDBOX_MODE` | `docker` / `local` / `cloud` | `local` |
| `JWT_SECRET` | JWT signing secret | (auto-generated) |

### Three Running Modes

1. **Localhost** — Local Ollama LLM, local sandbox, no cloud dependency
2. **Cascade** — Editor integration mode, connects to external IDE
3. **Cloud** — Remote VM sandbox with full Docker isolation

## First Session

1. Open OpenAgent (desktop app or http://localhost:3000)
2. Select your running mode (Localhost/Cascade/Cloud)
3. Type a request: e.g., "Create a FastAPI REST API with CRUD endpoints"
4. Watch the Agent plan, code, and test in the sandbox
5. Review changes in the Changes tab
6. Approve or request modifications

## Exploring Features

- **DeepWiki**: Navigate to Wiki in sidebar to browse auto-generated code documentation
- **CodeMap**: View code flow diagrams, dependency graphs, and metrics
- **Automations**: Set up PR auto-review, scheduled code scans, issue analysis
- **Settings**: Configure LLM models, security policies, environment blueprints
