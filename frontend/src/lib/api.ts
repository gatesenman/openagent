/**
 * API 客户端 / API client.
 *
 * 封装与后端 API 的通信。
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Session {
  id: string;
  title: string;
  status: string;
  mode: string;
  model: string;
  platform: string;
  language: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  session_id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface AgentEvent {
  type: string;
  message_id?: string;
  tool_call_id?: string;
  tool_name?: string;
  delta?: string;
  content?: string;
  error?: string;
  step?: string;
}

export interface SymbolDoc {
  symbol_name: string;
  symbol_kind: string;
  file_path: string;
  definition: string;
  example_usages: string[];
  notes: string[];
  see_also: string[];
  follow_up_questions: string[];
}

export interface FlowStep {
  step_number: number;
  title: string;
  description: string;
  source_file: string;
  source_lines: string;
  code_snippet: string;
  next_steps: number[];
}

/** 通用 fetch 封装 */
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/** Sessions API */
export const sessionsApi = {
  list: (skip = 0, limit = 20) =>
    apiFetch<{ sessions: Session[]; total: number }>(
      `/api/sessions?skip=${skip}&limit=${limit}`
    ),

  get: (id: string) => apiFetch<Session>(`/api/sessions/${id}`),

  create: (data: { title?: string; mode?: string; model?: string; prompt?: string }) =>
    apiFetch<Session>("/api/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiFetch<{ ok: boolean }>(`/api/sessions/${id}`, { method: "DELETE" }),

  getMessages: (id: string) =>
    apiFetch<{ messages: Message[] }>(`/api/sessions/${id}/messages`),
};

/** DeepWiki API */
export const deepwikiApi = {
  status: () => apiFetch<{ status: string; indexed_repos: number }>("/api/deepwiki"),

  indexRepo: (repoPath: string) =>
    apiFetch<{ total_files: number; indexed_files: number; total_symbols: number }>(
      "/api/deepwiki/index",
      { method: "POST", body: JSON.stringify({ repo_path: repoPath }) }
    ),

  listSymbols: (repoPath: string, kind?: string) =>
    apiFetch<{ symbols: SymbolDoc[]; total: number }>(
      `/api/deepwiki/symbols?repo_path=${encodeURIComponent(repoPath)}${kind ? `&kind=${kind}` : ""}`
    ),

  getSymbolDoc: (name: string, repoPath: string) =>
    apiFetch<SymbolDoc>(
      `/api/deepwiki/symbols/${name}?repo_path=${encodeURIComponent(repoPath)}`
    ),

  search: (query: string, topK = 10) =>
    apiFetch<{ results: Array<{ file_path: string; symbol_name: string; score: number }> }>(
      "/api/deepwiki/search",
      { method: "POST", body: JSON.stringify({ query, top_k: topK }) }
    ),
};

/** CodeMap API */
export const codemapApi = {
  analyze: (repoPath: string) =>
    apiFetch<{ modules: Array<Record<string, unknown>>; summary: Record<string, unknown> }>(
      "/api/codemaps/analyze",
      { method: "POST", body: JSON.stringify({ repo_path: repoPath }) }
    ),

  dependencies: (repoPath: string) =>
    apiFetch<{ nodes: unknown[]; edges: unknown[]; cycles: unknown[] }>(
      "/api/codemaps/dependencies",
      { method: "POST", body: JSON.stringify({ repo_path: repoPath }) }
    ),

  flow: (entryPoint: string, repoPath: string) =>
    apiFetch<{ steps: FlowStep[]; total_steps: number }>(
      "/api/codemaps/flow",
      { method: "POST", body: JSON.stringify({ entry_point: entryPoint, repo_path: repoPath }) }
    ),

  overview: (repoPath: string) =>
    apiFetch<Record<string, unknown>>(
      "/api/codemaps/overview",
      { method: "POST", body: JSON.stringify({ repo_path: repoPath }) }
    ),

  callgraph: (repoPath: string) =>
    apiFetch<{ functions: unknown[]; edges: unknown[]; stats: Record<string, unknown> }>(
      "/api/codemaps/callgraph",
      { method: "POST", body: JSON.stringify({ repo_path: repoPath }) }
    ),

  metrics: (repoPath: string) =>
    apiFetch<{ summary: Record<string, unknown>; files: unknown[]; by_language: Record<string, unknown> }>(
      "/api/codemaps/metrics",
      { method: "POST", body: JSON.stringify({ repo_path: repoPath }) }
    ),
};

/** Protocols API */
export const protocolsApi = {
  status: () =>
    apiFetch<{ protocols: Array<{ name: string; status: string }> }>(
      "/api/protocols"
    ),

  mcpInfo: () =>
    apiFetch<{ name: string; version: string; protocol_version: string }>(
      "/mcp/info"
    ),
};

/** SSE 事件流 */
export function subscribeChatSSE(
  sessionId: string,
  message: string,
  onEvent: (event: AgentEvent) => void,
  onError?: (err: Error) => void,
): AbortController {
  const controller = new AbortController();

  fetch(`${API_BASE}/api/sessions/${sessionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`SSE Error: ${res.status}`);
      const reader = res.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              onEvent(data);
            } catch {
              // skip invalid JSON
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError?.(err);
      }
    });

  return controller;
}

/** WebSocket 连接 */
export function connectTerminalWS(
  sessionId: string,
  onMessage: (data: Record<string, unknown>) => void,
  onError?: (err: Event) => void,
): WebSocket {
  const wsBase = API_BASE.replace(/^http/, "ws");
  const ws = new WebSocket(`${wsBase}/ws/terminal/${sessionId}`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // skip
    }
  };

  ws.onerror = (err) => onError?.(err);

  return ws;
}
