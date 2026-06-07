# API Reference

OpenAgent exposes 220+ API endpoints across REST, WebSocket, and SSE protocols.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All endpoints (except `/health` and `/auth/login`) require a Bearer token:

```
Authorization: Bearer <jwt_token>
```

## Core Endpoints

### Sessions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/sessions` | List all sessions |
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/{id}` | Get session details |
| DELETE | `/api/sessions/{id}` | Delete session |
| POST | `/api/sessions/{id}/message` | Send message to agent |
| POST | `/api/sessions/{id}/pause` | Pause session |
| POST | `/api/sessions/{id}/resume` | Resume session |
| POST | `/api/sessions/{id}/handoff` | Handoff to different mode |
| POST | `/api/sessions/{id}/fork` | Fork session |

### Agent Chat (SSE)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat/sse` | Stream agent responses via SSE |

### DeepWiki

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/deepwiki/symbols` | List indexed symbols |
| GET | `/api/deepwiki/symbols/{name}` | Get symbol documentation |
| POST | `/api/deepwiki/index` | Index a repository |
| POST | `/api/deepwiki/search` | Semantic search |

### CodeMap

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/codemap/analyze` | Analyze code structure |
| GET | `/api/codemap/dependencies` | Get dependency graph |
| GET | `/api/codemap/callgraph` | Get call graph |
| GET | `/api/codemap/metrics` | Get code metrics |
| GET | `/api/codemap/flow` | Get flow diagram |

### Security (Codex)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/codex/capabilities` | List security capabilities |
| POST | `/api/codex/scan/full` | Full security scan |
| POST | `/api/codex/scan/sast` | SAST scan |
| POST | `/api/codex/scan/secrets` | Secret detection scan |
| POST | `/api/codex/scan/dependencies` | SCA scan |
| POST | `/api/codex/scan/licenses` | License compliance scan |
| POST | `/api/codex/scan/iac` | IaC security scan |
| POST | `/api/codex/sbom` | Generate SBOM |
| POST | `/api/codex/compliance` | Compliance report |

### Automations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/automations` | List automation rules |
| POST | `/api/automations` | Create automation rule |
| PUT | `/api/automations/{id}` | Update rule |
| DELETE | `/api/automations/{id}` | Delete rule |
| POST | `/api/automations/{id}/toggle` | Toggle rule on/off |

### WebSocket Endpoints

| Path | Description |
|------|-------------|
| `/ws/terminal/{session_id}` | Real-time terminal stream |
| `/ws/events/{session_id}` | Agent event stream (16 event types) |
| `/ws/desktop/{session_id}` | Desktop VNC stream |

### Protocol Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/mcp/rpc` | MCP JSON-RPC 2.0 endpoint |
| GET | `/api/protocols` | List supported protocols |
| GET | `/llms.txt` | LLM-readable capabilities |
| GET | `/agents.txt` | Agent discovery |
| GET | `/.well-known/agent.json` | Agent metadata (MCP/A2A/AG-UI) |

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden (RBAC) |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |

## Rate Limits

- Default: 100 requests/minute per user
- Chat/SSE: 20 requests/minute per session
- Computer Use: 30 actions/minute per session
