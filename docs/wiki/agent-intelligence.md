# Agent Intelligence Modules

OpenAgent includes 7 specialized intelligence modules that enhance the core ReAct engine.

## 1. Terminal Stream (`terminal_stream.py`)

Real-time WebSocket-based terminal interaction with sandbox environments.

- PTY (pseudo-terminal) emulation for interactive shell sessions
- Dangerous command interception (rm -rf, DROP TABLE, etc.)
- Session history tracking and replay
- Bi-directional data flow: user input -> sandbox -> output stream

## 2. Evaluation Framework (`evaluation.py`)

SWE-bench style benchmarking system for measuring Agent quality.

- 5 built-in evaluation cases (bug fix, feature add, refactor, test writing, documentation)
- 6-dimension scoring: correctness, completeness, code quality, efficiency, safety, communication
- Suite-level execution with aggregate statistics
- Configurable benchmarks (swe-bench, humaneval, custom)

## 3. Anti-Hallucination Pipeline (`anti_hallucination.py`)

6-gate verification pipeline ensuring code correctness:

1. **Syntax Check** — Parse generated code for syntax errors
2. **Type Check** — Validate type annotations and usage
3. **Lint Check** — Run linter rules against generated code
4. **Unit Test** — Execute relevant unit tests
5. **Integration Test** — Verify cross-module interactions
6. **Self-Review** — LLM re-examines its own output for issues

Features:
- Up to 3 automatic fix attempts per gate failure
- Debug trace recording for each gate
- Configurable gate severity (error/warning/info)

## 4. Code Retrieval (`code_retrieval.py`)

Hybrid search pipeline for finding relevant code context:

1. **Intent Parsing** — Extract search keywords, file types, symbol names from query
2. **Dual Search** — BM25 (keyword) + Embedding (semantic) in parallel
3. **5-Factor Ranking** — Recency, relevance, file importance, symbol type, call frequency
4. **Token Budget** — Trim results to fit within LLM context window

## 5. Tool Output Guard (`tool_guard.py`)

Protects the Agent from processing bad tool outputs:

### Error Classification (8 types)
| Error Class | Action | Example |
|-------------|--------|---------|
| SCHEMA_MISMATCH | STOP_WITH_MESSAGE | Expected JSON, got HTML |
| PARTIAL_DATA | RETRY_WITH_HINT | Truncated API response |
| SEMANTIC_GARBAGE | STOP_WITH_MESSAGE | Valid JSON but meaningless content |
| TRANSIENT_FAILURE | AUTO_RETRY | Network timeout, 503 error |
| PERMISSION_DENIED | STOP_WITH_MESSAGE | 403 Forbidden |
| NOT_FOUND | STOP_WITH_MESSAGE | 404 Not Found |
| TIMEOUT | AUTO_RETRY | Command exceeded time limit |
| RATE_LIMIT | AUTO_RETRY | 429 Too Many Requests |

- Auto-retry with exponential backoff (max 3 attempts)
- Large output truncation (>50K tokens saved to temp file)
- Per-tool retry counter tracking

## 6. Computer Use (`computer_use.py`)

Browser/desktop automation via vision loop:

```
Screenshot -> Multimodal LLM Analysis -> Action Execution -> Screenshot
```

### Action Types
CLICK, DOUBLE_CLICK, RIGHT_CLICK, TYPE, KEY, SCROLL, SCREENSHOT, DRAG, WAIT, NAVIGATE

### Safety Guards
- **Domain Whitelist**: github.com, stackoverflow.com, docs.python.org, developer.mozilla.org, npmjs.com, pypi.org
- **Rate Limiting**: Max 30 actions per minute
- **Stuck Detection**: 3 identical consecutive actions triggers strategy change

### Backend Support
- CDP (Chrome DevTools Protocol)
- VNC
- Playwright

## 7. Multi-Agent Coordinator (`multi_agent.py`)

Orchestrates multiple specialized agents working on the same task:

### Agent Roles
| Role | Responsibility |
|------|---------------|
| COORDINATOR | Task decomposition, assignment, conflict resolution |
| CODE | Implementation, coding tasks |
| REVIEW | Code review, quality checks |
| TEST | Test writing, test execution |
| PLAN | Architecture planning |
| DEBUG | Error analysis, debugging |

### Task Pipeline
```
User Request -> Coordinator decomposes into sub-tasks:
  1. Plan (PLAN agent)
  2. Code (CODE agent) - depends on Plan
  3. Review (REVIEW agent) - depends on Code
  4. Test (TEST agent) - depends on Code
```

### Features
- Dependency-aware task scheduling (DAG)
- A2A messaging between agents
- Conflict detection and resolution (FILE_CONFLICT, DESIGN_DISAGREEMENT, DEPENDENCY_CONFLICT, TEST_FAILURE)
- Saga compensation: failure in one task auto-cancels dependent tasks
