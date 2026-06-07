# Architecture Overview

## System Architecture

OpenAgent follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│  Web (Next.js) │ Desktop (Tauri) │ CLI (Python)         │
├─────────────────────────────────────────────────────────┤
│                    API Gateway                           │
│  FastAPI (REST + WebSocket + SSE) │ 220+ routes          │
├─────────────────────────────────────────────────────────┤
│                  Core Services                           │
│  Agent Engine │ Sandbox │ Code Intelligence │ Platform   │
├─────────────────────────────────────────────────────────┤
│                  Protocol Layer                           │
│  MCP │ A2A │ AG-UI │ JSON-RPC 2.0                        │
├─────────────────────────────────────────────────────────┤
│                    Data Layer                             │
│  PostgreSQL │ SQLite │ Vector DB (Embedding)              │
└─────────────────────────────────────────────────────────┘
```

## Agent Engine

The ReAct (Reasoning + Acting) engine is the core of OpenAgent:

1. **Think** — LLM analyzes the current context and decides next action
2. **Act** — Execute tool call in sandboxed environment
3. **Observe** — Capture tool output and validate results
4. **Reflect** — Evaluate progress and decide whether to continue

### 7 Agent Intelligence Modules

| Module | Purpose |
|--------|---------|
| Terminal Stream | WebSocket PTY for real-time sandbox interaction |
| Evaluation Framework | SWE-bench style benchmarking with 6-dimension scoring |
| Anti-Hallucination | 6-gate verification pipeline (syntax, type, lint, unit test, integration, self-review) |
| Code Retrieval | BM25 + embedding hybrid search with 5-factor ranking |
| Tool Output Guard | Error classification (8 types) + retry/stop/truncate strategies |
| Computer Use | Vision loop (screenshot -> multimodal LLM -> action -> screenshot) |
| Multi-Agent Coordinator | Task decomposition, dependency tracking, Saga compensation |

## Sandbox Virtualization

Every Agent session runs inside an isolated environment:

- **Docker Sandbox** — Production: full container isolation per session
- **Local Sandbox** — Development: subprocess-based execution
- **Cloud Sandbox** — Remote VM with VNC desktop streaming

### Sandbox Capabilities

- Shell command execution (with dangerous command interception)
- File system read/write (scoped to workspace)
- Git operations (clone, commit, push, PR creation)
- Terminal streaming via WebSocket
- Desktop streaming via VNC (Phase 2)

## Code Intelligence

### DeepWiki
Automatic symbol-level documentation generation:
- AST parsing via tree-sitter (with regex fallback)
- 5-section format: Definition / Examples / Notes / See Also / Follow-up Questions
- Embedding-based semantic search
- Cross-reference analysis

### CodeMap
Code structure visualization:
- Flow diagrams (numbered steps with source references)
- Dependency graphs (with cycle detection)
- Call graphs (function-level)
- Code metrics (cyclomatic complexity, LOC, comment ratio)

## Security

### Codex Security Engine
Enterprise-grade code security analysis:
- **SAST**: 12 rules covering 12 CWEs
- **SCA**: Dependency vulnerability scanning
- **Secret Detection**: 17 patterns (AWS, GitHub, Stripe, etc.)
- **License Compliance**: 14 license types with policy enforcement
- **IaC Security**: Docker/Kubernetes/Terraform scanning
- **SBOM**: CycloneDX 1.5 format generation
- **Compliance**: SOC2, ISO27001, GDPR, HIPAA, PCI DSS, NIST 800-53

### OWASP LLM Top 10 (2025)
Protection against all 10 categories including Prompt Injection, Insecure Output Handling, and Supply Chain Vulnerabilities.
