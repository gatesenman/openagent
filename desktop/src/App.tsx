/**
 * OpenAgent Desktop Client
 *
 * Cross-platform AI Code Agent with embedded virtual environment.
 * Supports: localhost (Docker sandbox), cascade (editor integration), cloud (remote).
 * Built with Tauri 2.x + React + Vite.
 */

import React, { useState, useEffect } from "react";

interface AppConfig {
  api_url: string;
  mode: string;
  language: string;
  theme: string;
}

interface PlatformInfo {
  os: string;
  arch: string;
  family: string;
}

declare global {
  interface Window {
    __TAURI__?: {
      core: {
        invoke: (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;
      };
    };
  }
}

async function invoke<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (window.__TAURI__) {
    return window.__TAURI__.core.invoke(cmd, args) as Promise<T>;
  }
  if (cmd === "get_config") return { api_url: "http://localhost:8000", mode: "localhost", language: "zh", theme: "dark" } as T;
  if (cmd === "get_platform_info") return { os: "windows", arch: "x86_64", family: "windows" } as T;
  return {} as T;
}

/* ── SVG Icons (inline, no emoji) ── */
function IconChat({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>);
}
function IconBook({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>);
}
function IconPlay({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>);
}
function IconChart({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>);
}
function IconGear({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>);
}
function IconTerminal({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>);
}
function IconZap({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>);
}
function IconGlobe({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>);
}
function IconBox({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>);
}
function IconCpu({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>);
}
function IconRefresh({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>);
}
function IconShield({ size = 16 }: { size?: number }) {
  return (<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>);
}

/* ── Status Dot ── */
function StatusDot({ color }: { color: string }) {
  return (
    <span style={{
      display: "inline-block", width: 8, height: 8, borderRadius: "50%",
      backgroundColor: color, marginRight: 6, boxShadow: `0 0 4px ${color}40`,
    }} />
  );
}

/* ── Main App ── */
export default function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [platform, setPlatform] = useState<PlatformInfo | null>(null);
  const [health, setHealth] = useState<string>("checking");
  const [mode, setMode] = useState<string>("localhost");
  const [activeTab, setActiveTab] = useState<string>("sessions");

  useEffect(() => {
    invoke<AppConfig>("get_config").then(setConfig);
    invoke<PlatformInfo>("get_platform_info").then(setPlatform);
  }, []);

  useEffect(() => {
    const url = config?.api_url || "http://localhost:8000";
    const check = () => {
      invoke<Record<string, unknown>>("check_health", { apiUrl: url })
        .then(() => setHealth("connected"))
        .catch(() => setHealth("disconnected"));
    };
    check();
    const timer = setInterval(check, 15000);
    return () => clearInterval(timer);
  }, [config]);

  return (
    <div style={{ fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", backgroundColor: "#0a0a1a", color: "#e0e0e0", height: "100vh", display: "flex", flexDirection: "column" }}>

      {/* ── Title Bar ── */}
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 16px", backgroundColor: "#0c0c14", borderBottom: "1px solid #1a1a2e", WebkitAppRegion: "drag" as never }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 24, height: 24, borderRadius: 6, backgroundColor: "#7c6ef0", color: "#fff", fontSize: 11, fontWeight: 700 }}>OA</span>
          <span style={{ fontWeight: 600, fontSize: 13, letterSpacing: 0.3 }}>OpenAgent</span>
          <span style={{ fontSize: 10, padding: "1px 6px", borderRadius: 3, backgroundColor: mode === "cloud" ? "#1a3a5a" : mode === "cascade" ? "#3a2a1a" : "#1a3a2a", color: mode === "cloud" ? "#60a5fa" : mode === "cascade" ? "#f59e0b" : "#4ade80" }}>
            {mode.toUpperCase()}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 11 }}>
          <span style={{ display: "flex", alignItems: "center" }}>
            <StatusDot color={health === "connected" ? "#4ade80" : health === "checking" ? "#eab308" : "#666"} />
            {health === "connected" ? "Connected" : health === "checking" ? "Checking..." : "Offline"}
          </span>
          {platform && <span style={{ color: "#555" }}>{platform.os}/{platform.arch}</span>}
        </div>
      </header>

      {/* ── Main Layout ── */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>

        {/* Sidebar */}
        <nav style={{ width: 52, backgroundColor: "#0c0c14", borderRight: "1px solid #1a1a2e", display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 8 }}>
          <SidebarIcon icon={<IconChat size={18} />} label="Sessions" active={activeTab === "sessions"} onClick={() => setActiveTab("sessions")} />
          <SidebarIcon icon={<IconBook size={18} />} label="Wiki" active={activeTab === "wiki"} onClick={() => setActiveTab("wiki")} />
          <SidebarIcon icon={<IconShield size={18} />} label="Review" active={activeTab === "review"} onClick={() => setActiveTab("review")} />
          <SidebarIcon icon={<IconZap size={18} />} label="Auto" active={activeTab === "automations"} onClick={() => setActiveTab("automations")} />
          <SidebarIcon icon={<IconChart size={18} />} label="Analytics" active={activeTab === "analytics"} onClick={() => setActiveTab("analytics")} />
          <div style={{ flex: 1 }} />
          <SidebarIcon icon={<IconGear size={18} />} label="Settings" active={activeTab === "settings"} onClick={() => setActiveTab("settings")} />
          <div style={{ marginBottom: 8 }}>
            <StatusDot color={health === "connected" ? "#4ade80" : "#555"} />
          </div>
        </nav>

        {/* Content Area */}
        <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", backgroundColor: "#111119" }}>
          {activeTab === "sessions" && <SessionsView mode={mode} setMode={setMode} apiUrl={config?.api_url || "http://localhost:8000"} health={health} />}
          {activeTab === "wiki" && <WikiView />}
          {activeTab === "review" && <ReviewView />}
          {activeTab === "automations" && <AutomationsView />}
          {activeTab === "analytics" && <AnalyticsView />}
          {activeTab === "settings" && <SettingsView config={config} />}
        </main>
      </div>

      {/* ── Status Bar ── */}
      <footer style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "3px 12px", backgroundColor: "#0c0c14", borderTop: "1px solid #1a1a2e", fontSize: 10, color: "#444" }}>
        <span>OpenAgent v0.1.0</span>
        <span>{config?.api_url || "http://localhost:8000"} | {mode} | {config?.language || "zh"}</span>
      </footer>
    </div>
  );
}

/* ── Sidebar Icon Button ── */
function SidebarIcon({ icon, label, active, onClick }: { icon: React.ReactNode; label: string; active?: boolean; onClick?: () => void }) {
  return (
    <button onClick={onClick} title={label} style={{
      display: "flex", alignItems: "center", justifyContent: "center",
      width: 36, height: 36, borderRadius: 8, border: "none", cursor: "pointer",
      backgroundColor: active ? "#7c6ef020" : "transparent",
      color: active ? "#7c6ef0" : "#666",
      marginBottom: 4, position: "relative",
      borderLeft: active ? "2px solid #7c6ef0" : "2px solid transparent",
    }}>
      {icon}
    </button>
  );
}

/* ── Sessions View ── */
function SessionsView({ mode, setMode, apiUrl, health }: { mode: string; setMode: (m: string) => void; apiUrl: string; health: string }) {
  const [sessions] = useState([
    { id: "s1", title: "Implement user auth module", status: "running", model: "deepseek-v3", created: "2026-06-06 15:30" },
    { id: "s2", title: "Fix API performance issue", status: "completed", model: "gpt-4o", created: "2026-06-06 14:00" },
    { id: "s3", title: "Refactor data layer", status: "paused", model: "qwen-72b", created: "2026-06-06 12:20" },
  ]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [input, setInput] = useState("");

  const statusColors: Record<string, string> = { running: "#10b981", completed: "#3b82f6", paused: "#eab308", failed: "#ef4444" };

  return (
    <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
      {/* Session List (left panel) */}
      <div style={{ width: 260, borderRight: "1px solid #1a1a2e", display: "flex", flexDirection: "column", backgroundColor: "#0d0d17" }}>
        <div style={{ padding: "10px 12px", borderBottom: "1px solid #1a1a2e", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1, color: "#888" }}>Sessions</span>
          <button style={{ background: "#7c6ef0", border: "none", color: "#fff", padding: "3px 10px", borderRadius: 4, fontSize: 11, cursor: "pointer" }}>+ New</button>
        </div>
        <div style={{ flex: 1, overflowY: "auto" }}>
          {sessions.map((s) => (
            <button key={s.id} onClick={() => setSelectedSession(s.id)} style={{
              display: "block", width: "100%", textAlign: "left", padding: "10px 12px",
              border: "none", borderBottom: "1px solid #1a1a2e", cursor: "pointer",
              backgroundColor: selectedSession === s.id ? "#1a1a2e" : "transparent", color: "#e0e0e0",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3 }}>
                <StatusDot color={statusColors[s.status] || "#666"} />
                <span style={{ fontSize: 12, fontWeight: 500 }}>{s.title}</span>
              </div>
              <div style={{ fontSize: 10, color: "#555", paddingLeft: 14 }}>{s.model} | {s.created}</div>
            </button>
          ))}
        </div>

        {/* Mode Selector */}
        <div style={{ padding: 8, borderTop: "1px solid #1a1a2e" }}>
          <div style={{ display: "flex", gap: 4 }}>
            {(["localhost", "cascade", "cloud"] as const).map((m) => (
              <button key={m} onClick={() => setMode(m)} style={{
                flex: 1, padding: "4px 0", fontSize: 10, border: "1px solid", borderRadius: 4, cursor: "pointer",
                backgroundColor: mode === m ? "#7c6ef015" : "transparent",
                borderColor: mode === m ? "#7c6ef040" : "#1a1a2e",
                color: mode === m ? "#7c6ef0" : "#666",
              }}>
                {m === "localhost" && <IconTerminal size={10} />}
                {m === "cascade" && <IconZap size={10} />}
                {m === "cloud" && <IconGlobe size={10} />}
                {" "}{m}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Session Detail (right panel) */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {selectedSession ? (
          <>
            {/* Tab bar */}
            <div style={{ display: "flex", borderBottom: "1px solid #1a1a2e", backgroundColor: "#0d0d17" }}>
              {["Chat", "Worklog", "Terminal", "Changes", "Desktop"].map((tab) => (
                <button key={tab} style={{
                  padding: "8px 16px", border: "none", cursor: "pointer", fontSize: 11,
                  backgroundColor: tab === "Chat" ? "#111119" : "transparent",
                  color: tab === "Chat" ? "#e0e0e0" : "#666",
                  borderBottom: tab === "Chat" ? "2px solid #7c6ef0" : "2px solid transparent",
                }}>{tab}</button>
              ))}
            </div>

            {/* Chat area */}
            <div style={{ flex: 1, padding: 16, overflowY: "auto" }}>
              <div style={{ maxWidth: 640, margin: "0 auto" }}>
                <div style={{ padding: 12, borderRadius: 8, backgroundColor: "#1a1a2e", marginBottom: 12 }}>
                  <div style={{ fontSize: 10, color: "#7c6ef0", marginBottom: 4, fontWeight: 600 }}>USER</div>
                  <div style={{ fontSize: 13 }}>Implement user authentication with JWT tokens and RBAC</div>
                </div>
                <div style={{ padding: 12, borderRadius: 8, backgroundColor: "#0d1a0d", border: "1px solid #1a3a2a", marginBottom: 12 }}>
                  <div style={{ fontSize: 10, color: "#4ade80", marginBottom: 4, fontWeight: 600 }}>AGENT</div>
                  <div style={{ fontSize: 13 }}>I'll implement JWT authentication with role-based access control. Let me start by analyzing the current codebase structure...</div>
                  <div style={{ marginTop: 8, padding: 8, borderRadius: 4, backgroundColor: "#0a0a1a", fontFamily: "monospace", fontSize: 11, color: "#4ade80" }}>
                    $ git status<br/>
                    $ python -m pytest tests/ -v<br/>
                    <span style={{ color: "#888" }}>// 3 files changed, 142 insertions</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Input */}
            <div style={{ padding: "8px 12px", borderTop: "1px solid #1a1a2e" }}>
              <div style={{ display: "flex", gap: 8 }}>
                <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type a message..." style={{
                  flex: 1, padding: "8px 12px", backgroundColor: "#0d0d17", border: "1px solid #1a1a2e",
                  borderRadius: 6, color: "#e0e0e0", fontSize: 12, outline: "none",
                }} />
                <button style={{ padding: "8px 16px", backgroundColor: "#7c6ef0", border: "none", borderRadius: 6, color: "#fff", fontSize: 12, cursor: "pointer" }}>Send</button>
              </div>
            </div>
          </>
        ) : (
          /* Empty state with session prompt */
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 48, height: 48, borderRadius: 12, backgroundColor: "#7c6ef0", marginBottom: 16 }}>
              <span style={{ color: "#fff", fontWeight: 700, fontSize: 18 }}>OA</span>
            </div>
            <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 4 }}>OpenAgent</h2>
            <p style={{ fontSize: 11, color: "#666", textTransform: "uppercase", letterSpacing: 1, marginBottom: 24 }}>Cross-Platform Code Agent Desktop</p>

            <div style={{ width: 480, maxWidth: "90%" }}>
              <div style={{ position: "relative", backgroundColor: "#0d0d17", border: "1px solid #1a1a2e", borderRadius: 8, overflow: "hidden", marginBottom: 16 }}>
                <textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="Describe your task... Agent will execute in sandbox" rows={3} style={{
                  width: "100%", padding: "12px", backgroundColor: "transparent", border: "none", color: "#e0e0e0", fontSize: 13, resize: "none", outline: "none",
                }} />
                <div style={{ display: "flex", justifyContent: "space-between", padding: "4px 12px 8px", alignItems: "center" }}>
                  <span style={{ fontSize: 10, color: "#555" }}>Shift+Enter for new line</span>
                  <button disabled={!input.trim()} style={{ padding: "4px 14px", backgroundColor: input.trim() ? "#7c6ef0" : "#333", border: "none", borderRadius: 4, color: "#fff", fontSize: 11, cursor: input.trim() ? "pointer" : "default", opacity: input.trim() ? 1 : 0.4 }}>Start Session</button>
                </div>
              </div>

              {/* Feature cards */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                <FeatureCard icon={<IconBox size={18} />} title="Docker Sandbox" desc="Isolated container per session" />
                <FeatureCard icon={<IconCpu size={18} />} title="Multi-Model" desc="GPT-4o / DeepSeek / Qwen" />
                <FeatureCard icon={<IconRefresh size={18} />} title="Mode Switch" desc="Local / Cloud seamless handoff" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Wiki View ── */
function WikiView() {
  const symbols = [
    { name: "ReactEngine", kind: "class", path: "agent/react_engine.py" },
    { name: "DockerSandbox", kind: "class", path: "sandbox/docker_sandbox.py" },
    { name: "SessionService", kind: "class", path: "services/session_service.py" },
    { name: "CodeParser", kind: "class", path: "services/deepwiki/parser.py" },
    { name: "FlowGenerator", kind: "class", path: "services/codemap/flow_gen.py" },
  ];
  const [selected, setSelected] = useState("ReactEngine");

  return (
    <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
      <div style={{ width: 280, borderRight: "1px solid #1a1a2e", overflowY: "auto", backgroundColor: "#0d0d17" }}>
        <div style={{ padding: "10px 12px", borderBottom: "1px solid #1a1a2e" }}>
          <span style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1, color: "#888" }}>DeepWiki</span>
          <input placeholder="Search symbols..." style={{ width: "100%", marginTop: 8, padding: "6px 10px", backgroundColor: "#111119", border: "1px solid #1a1a2e", borderRadius: 4, color: "#e0e0e0", fontSize: 11, outline: "none" }} />
        </div>
        {symbols.map((s) => (
          <button key={s.name} onClick={() => setSelected(s.name)} style={{
            display: "block", width: "100%", textAlign: "left", padding: "10px 12px",
            border: "none", borderBottom: "1px solid #1a1a2e", cursor: "pointer",
            backgroundColor: selected === s.name ? "#7c6ef010" : "transparent", color: "#e0e0e0",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
              <span style={{ fontSize: 9, padding: "1px 5px", borderRadius: 3, backgroundColor: "#7c6ef020", color: "#7c6ef0" }}>{s.kind}</span>
              <span style={{ fontSize: 12, fontWeight: 500 }}>{s.name}</span>
            </div>
            <div style={{ fontSize: 10, color: "#555" }}>{s.path}</div>
          </button>
        ))}
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: 24 }}>
        <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>{selected}</h2>
        <Section title="Definition" color="#7c6ef0">
          <p style={{ fontSize: 13, lineHeight: 1.6 }}>
            <code>{selected}</code> is the core Agent engine implementing ReAct (Reasoning + Acting) loop.
            Each iteration cycles through Think, Act, Observe, Reflect phases.
          </p>
        </Section>
        <Section title="Example Usage" color="#7c6ef0">
          <pre style={{ padding: 12, borderRadius: 6, backgroundColor: "#0a0a14", fontSize: 11, fontFamily: "monospace", color: "#4ade80", overflow: "auto" }}>
{`engine = ReactEngine(sandbox=sandbox, llm_client=client)
async for event in engine.run(messages, session_id="abc"):
    print(event.type, event.data)`}
          </pre>
        </Section>
        <Section title="Notes" color="#7c6ef0">
          <ul style={{ fontSize: 12, lineHeight: 1.8, paddingLeft: 16, color: "#ccc" }}>
            <li>Max iterations default: 50, auto-switches strategy after 3 consecutive errors</li>
            <li>All tool calls execute inside sandboxed virtual environment</li>
          </ul>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <h3 style={{ fontSize: 14, fontWeight: 600, color, marginBottom: 8 }}>{title}</h3>
      {children}
    </div>
  );
}

/* ── Review View ── */
function ReviewView() {
  const reviews = [
    { id: "PR-42", title: "Add user authentication", repo: "openagent/backend", status: "pending", risk: "medium", files: 8 },
    { id: "PR-41", title: "Fix database migration", repo: "openagent/backend", status: "approved", risk: "low", files: 3 },
    { id: "PR-40", title: "Update dependencies", repo: "openagent/frontend", status: "changes_requested", risk: "high", files: 2 },
  ];
  const riskColors: Record<string, string> = { low: "#4ade80", medium: "#eab308", high: "#ef4444" };
  const statusColors: Record<string, string> = { pending: "#eab308", approved: "#4ade80", changes_requested: "#ef4444" };

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>Review</h2>
      <p style={{ fontSize: 12, color: "#666", marginBottom: 20 }}>Agent-powered PR review with security analysis and code quality checks.</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {reviews.map((pr) => (
          <div key={pr.id} style={{ padding: 14, backgroundColor: "#0d0d17", borderRadius: 8, border: "1px solid #1a1a2e", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: 13, fontWeight: 500 }}>{pr.title}</span>
                <span style={{ fontSize: 10, color: "#666", fontFamily: "monospace" }}>{pr.id}</span>
              </div>
              <span style={{ fontSize: 10, color: "#555" }}>{pr.repo} | {pr.files} files</span>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, backgroundColor: `${riskColors[pr.risk]}20`, color: riskColors[pr.risk] }}>{pr.risk}</span>
              <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, backgroundColor: `${statusColors[pr.status]}20`, color: statusColors[pr.status] }}>{pr.status.replace("_", " ")}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Automations View ── */
function AutomationsView() {
  const [rules] = useState([
    { id: "1", name: "PR Auto Review", trigger: "pr_opened", action: "auto_review", enabled: true },
    { id: "2", name: "Daily Code Scan", trigger: "schedule", action: "code_scan", enabled: true },
    { id: "3", name: "Issue Auto Analyze", trigger: "issue_created", action: "analyze_issue", enabled: false },
    { id: "4", name: "Webhook Deploy Notify", trigger: "webhook", action: "notify_deploy", enabled: true },
  ]);

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>Automations</h2>
          <p style={{ fontSize: 12, color: "#666" }}>Event-driven automation rules for CI/CD and code operations.</p>
        </div>
        <button style={{ padding: "6px 14px", backgroundColor: "#7c6ef0", border: "none", borderRadius: 6, color: "#fff", fontSize: 11, cursor: "pointer" }}>+ Create Rule</button>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {rules.map((r) => (
          <div key={r.id} style={{ padding: 14, backgroundColor: "#0d0d17", borderRadius: 8, border: "1px solid #1a1a2e", opacity: r.enabled ? 1 : 0.5, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 9, fontFamily: "monospace", padding: "2px 6px", borderRadius: 3, backgroundColor: "#7c6ef015", color: "#7c6ef0" }}>{r.trigger.toUpperCase().slice(0, 3)}</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{r.name}</div>
                <div style={{ fontSize: 10, color: "#555" }}>Trigger: {r.trigger} | Action: {r.action}</div>
              </div>
            </div>
            <div style={{ width: 36, height: 18, borderRadius: 9, backgroundColor: r.enabled ? "#7c6ef0" : "#333", position: "relative", cursor: "pointer" }}>
              <div style={{ position: "absolute", top: 2, width: 14, height: 14, borderRadius: 7, backgroundColor: "#fff", left: r.enabled ? 20 : 2, transition: "left 0.2s" }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Analytics View ── */
function AnalyticsView() {
  return (
    <div style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 20 }}>Analytics</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 24 }}>
        <StatCard label="Total Sessions" value="127" change="+12%" />
        <StatCard label="Tokens Used" value="2.4M" change="+8%" />
        <StatCard label="Success Rate" value="94.2%" change="+3%" />
      </div>
      <div style={{ padding: 24, backgroundColor: "#0d0d17", borderRadius: 8, border: "1px solid #1a1a2e", textAlign: "center" }}>
        <IconChart size={32} />
        <p style={{ fontSize: 12, color: "#666", marginTop: 8 }}>Usage trends and session analytics</p>
      </div>
    </div>
  );
}

function StatCard({ label, value, change }: { label: string; value: string; change: string }) {
  return (
    <div style={{ padding: 16, backgroundColor: "#0d0d17", borderRadius: 8, border: "1px solid #1a1a2e" }}>
      <div style={{ fontSize: 10, color: "#666", marginBottom: 4, textTransform: "uppercase" }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color: "#e0e0e0" }}>{value}</div>
      <div style={{ fontSize: 10, color: "#4ade80", marginTop: 2 }}>{change}</div>
    </div>
  );
}

/* ── Feature Card ── */
function FeatureCard({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div style={{ padding: 12, backgroundColor: "#0d0d17", borderRadius: 8, border: "1px solid #1a1a2e" }}>
      <div style={{ marginBottom: 6, color: "#7c6ef0" }}>{icon}</div>
      <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 2 }}>{title}</div>
      <div style={{ fontSize: 10, color: "#666" }}>{desc}</div>
    </div>
  );
}

/* ── Settings View ── */
function SettingsView({ config }: { config: AppConfig | null }) {
  const [activeSettingsTab, setActiveSettingsTab] = useState("general");

  const groups = [
    { label: "Personal", items: [{ key: "general", label: "General" }, { key: "connections", label: "Connections" }] },
    { label: "Organization", items: [{ key: "sessions", label: "Sessions" }, { key: "plans", label: "Plans & Billing" }, { key: "membership", label: "Membership" }, { key: "apikeys", label: "API Keys" }] },
    { label: "Agent", items: [{ key: "agent", label: "Agent Config" }, { key: "review", label: "Review" }, { key: "deepwiki", label: "DeepWiki" }, { key: "desktop", label: "Desktop" }] },
    { label: "Configuration", items: [{ key: "skills", label: "Skills & Rules" }, { key: "environment", label: "Environment" }, { key: "knowledge", label: "Knowledge" }, { key: "secrets", label: "Secrets" }, { key: "security", label: "Security" }] },
  ];

  return (
    <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
      <div style={{ width: 180, borderRight: "1px solid #1a1a2e", overflowY: "auto", padding: 8, backgroundColor: "#0d0d17" }}>
        <div style={{ padding: "8px 8px 12px", fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1, color: "#888" }}>Settings</div>
        {groups.map((g) => (
          <div key={g.label} style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 9, color: "#555", textTransform: "uppercase", letterSpacing: 1, padding: "0 8px", marginBottom: 4 }}>{g.label}</div>
            {g.items.map((item) => (
              <button key={item.key} onClick={() => setActiveSettingsTab(item.key)} style={{
                display: "block", width: "100%", textAlign: "left", padding: "4px 8px", border: "none",
                borderRadius: 4, fontSize: 11, cursor: "pointer",
                backgroundColor: activeSettingsTab === item.key ? "#7c6ef015" : "transparent",
                color: activeSettingsTab === item.key ? "#7c6ef0" : "#888",
              }}>{item.label}</button>
            ))}
          </div>
        ))}
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: 24 }}>
        <div style={{ maxWidth: 560 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, textTransform: "capitalize" }}>{activeSettingsTab.replace(/([A-Z])/g, " $1")}</h3>
          <SettingGroup title="General">
            <SettingRow label="API URL" value={config?.api_url || "http://localhost:8000"} />
            <SettingRow label="Language" value={config?.language || "zh"} />
            <SettingRow label="Theme" value={config?.theme || "dark"} />
          </SettingGroup>
          <SettingGroup title="Model">
            <SettingRow label="Default Model" value="auto (intelligent routing)" />
            <SettingRow label="Fallback Models" value="deepseek-v3, gpt-4o, qwen-72b" />
          </SettingGroup>
          <SettingGroup title="Sandbox">
            <SettingRow label="Platform" value="ubuntu-22.04" />
            <SettingRow label="CPU" value="4 cores" />
            <SettingRow label="Memory" value="8 GB" />
            <SettingRow label="Disk" value="50 GB" />
          </SettingGroup>
          <SettingGroup title="Security">
            <SettingRow label="RBAC" value="admin" />
            <SettingRow label="Command Interception" value="Enabled" />
            <SettingRow label="Network Filter" value="Allowlist" />
          </SettingGroup>
        </div>
      </div>
    </div>
  );
}

function SettingGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 16, backgroundColor: "#0d0d17", borderRadius: 8, border: "1px solid #1a1a2e", padding: 14 }}>
      <h4 style={{ fontSize: 11, fontWeight: 600, marginBottom: 10, color: "#888", textTransform: "uppercase", letterSpacing: 0.5 }}>{title}</h4>
      {children}
    </div>
  );
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "5px 0", borderBottom: "1px solid #1a1a2e" }}>
      <span style={{ fontSize: 12, color: "#888" }}>{label}</span>
      <span style={{ fontSize: 12, color: "#e0e0e0" }}>{value}</span>
    </div>
  );
}
