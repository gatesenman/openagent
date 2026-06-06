/**
 * OpenAgent 桌面客户端主界面
 *
 * 支持三种模式:
 * - localhost: 本地 Docker 沙箱开发
 * - cascade: Windsurf 集成模式
 * - cloud: 远程云端服务器
 *
 * 通过 Tauri IPC 调用 Rust 后端，
 * Rust 后端调用 FastAPI 服务器。
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
  // Web fallback for development
  console.warn(`Tauri not available, command: ${cmd}`);
  return {} as T;
}

export default function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [platform, setPlatform] = useState<PlatformInfo | null>(null);
  const [health, setHealth] = useState<string>("checking");
  const [mode, setMode] = useState<string>("localhost");
  const [activeTab, setActiveTab] = useState<string>("sessions");

  useEffect(() => {
    // 初始化
    invoke<AppConfig>("get_config").then(setConfig);
    invoke<PlatformInfo>("get_platform_info").then(setPlatform);
  }, []);

  useEffect(() => {
    if (config) {
      invoke<Record<string, unknown>>("check_health", { apiUrl: config.api_url })
        .then(() => setHealth("connected"))
        .catch(() => setHealth("disconnected"));
    }
  }, [config]);

  return (
    <div
      style={{
        fontFamily: "system-ui, -apple-system, sans-serif",
        backgroundColor: "#0a0a1a",
        color: "#e0e0e0",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Title bar */}
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 16px",
          backgroundColor: "#111127",
          borderBottom: "1px solid #1e1e3a",
          WebkitAppRegion: "drag" as never,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 18 }}>🤖</span>
          <span style={{ fontWeight: 600, fontSize: 14 }}>OpenAgent</span>
          <span
            style={{
              fontSize: 10,
              padding: "2px 6px",
              borderRadius: 4,
              backgroundColor: mode === "cloud" ? "#1a3a5a" : "#1a3a2a",
              color: mode === "cloud" ? "#60a5fa" : "#4ade80",
            }}
          >
            {mode.toUpperCase()}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 11 }}>
          <span>
            {health === "connected" ? "🟢" : health === "checking" ? "🟡" : "🔴"}{" "}
            {health === "connected" ? "已连接" : health === "checking" ? "检查中" : "未连接"}
          </span>
          {platform && (
            <span style={{ color: "#666" }}>
              {platform.os}/{platform.arch}
            </span>
          )}
        </div>
      </header>

      {/* Main content */}
      <div style={{ flex: 1, display: "flex" }}>
        {/* Sidebar */}
        <nav
          style={{
            width: 220,
            backgroundColor: "#0d0d20",
            borderRight: "1px solid #1e1e3a",
            padding: "12px 0",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <SidebarItem icon="💬" label="会话" active={activeTab === "sessions"} onClick={() => setActiveTab("sessions")} />
          <SidebarItem icon="📚" label="知识库" active={activeTab === "knowledge"} onClick={() => setActiveTab("knowledge")} />
          <SidebarItem icon="📖" label="Playbooks" active={activeTab === "playbooks"} onClick={() => setActiveTab("playbooks")} />
          <SidebarItem icon="📊" label="分析" active={activeTab === "analytics"} onClick={() => setActiveTab("analytics")} />
          <SidebarItem icon="⚙️" label="设置" active={activeTab === "settings"} onClick={() => setActiveTab("settings")} />
          <div style={{ flex: 1 }} />

          {/* Mode switcher */}
          <div style={{ padding: "8px 12px" }}>
            <div
              style={{
                fontSize: 10,
                color: "#666",
                marginBottom: 4,
                textTransform: "uppercase",
              }}
            >
              运行模式
            </div>
            {(["localhost", "cascade", "cloud"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  padding: "4px 8px",
                  fontSize: 12,
                  border: "none",
                  borderRadius: 4,
                  cursor: "pointer",
                  backgroundColor: mode === m ? "#1e1e3a" : "transparent",
                  color: mode === m ? "#60a5fa" : "#888",
                  marginBottom: 2,
                }}
              >
                {m === "localhost" ? "🖥️ " : m === "cascade" ? "🌊 " : "☁️ "}
                {m}
              </button>
            ))}
          </div>
        </nav>

        {/* Content area */}
        <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {activeTab === "sessions" && <SessionsView mode={mode} apiUrl={config?.api_url || "http://localhost:8000"} />}
          {activeTab === "knowledge" && <PlaceholderView title="知识库" desc="管理项目知识、最佳实践和约定" icon="📚" />}
          {activeTab === "playbooks" && <PlaceholderView title="Playbooks" desc="任务模板和工作流程" icon="📖" />}
          {activeTab === "analytics" && <PlaceholderView title="分析" desc="会话用量、生产力和成本统计" icon="📊" />}
          {activeTab === "settings" && <SettingsView config={config} />}
        </main>
      </div>

      {/* Status bar */}
      <footer
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "4px 12px",
          backgroundColor: "#111127",
          borderTop: "1px solid #1e1e3a",
          fontSize: 11,
          color: "#555",
        }}
      >
        <span>OpenAgent v0.1.0</span>
        <span>
          {config?.api_url || "http://localhost:8000"} | {mode} |{" "}
          {config?.language || "zh"}
        </span>
      </footer>
    </div>
  );
}

function SidebarItem({
  icon,
  label,
  active,
  onClick,
}: {
  icon: string;
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "8px 16px",
        border: "none",
        backgroundColor: active ? "#1e1e3a" : "transparent",
        color: active ? "#e0e0e0" : "#888",
        cursor: "pointer",
        fontSize: 13,
        textAlign: "left",
        width: "100%",
      }}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </button>
  );
}

function FeatureCard({ icon, title, desc }: { icon: string; title: string; desc: string }) {
  return (
    <div style={{ padding: 12, backgroundColor: "#111127", borderRadius: 8, border: "1px solid #1e1e3a" }}>
      <div style={{ fontSize: 20, marginBottom: 4 }}>{icon}</div>
      <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 2 }}>{title}</div>
      <div style={{ fontSize: 11, color: "#666" }}>{desc}</div>
    </div>
  );
}

function SessionsView({ mode, apiUrl }: { mode: string; apiUrl: string }) {
  const [sessions] = useState([
    { id: "s1", title: "修复登录bug", status: "running", model: "deepseek-v3", created: "2026-06-06 15:30" },
    { id: "s2", title: "添加用户配置页", status: "completed", model: "gpt-4o", created: "2026-06-06 14:00" },
    { id: "s3", title: "重构数据层", status: "paused", model: "qwen-72b", created: "2026-06-06 12:20" },
  ]);

  const statusColors: Record<string, string> = { running: "#10b981", completed: "#3b82f6", paused: "#eab308", failed: "#ef4444" };
  const statusLabels: Record<string, string> = { running: "运行中", completed: "已完成", paused: "已暂停", failed: "失败" };

  return (
    <div style={{ flex: 1, overflow: "auto", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600 }}>会话 ({mode})</h2>
        <button style={{ padding: "6px 16px", backgroundColor: "#3b82f6", color: "white", border: "none", borderRadius: 6, fontSize: 12, cursor: "pointer" }}>
          + 新建会话
        </button>
      </div>

      {sessions.length === 0 ? (
        <div style={{ textAlign: "center", paddingTop: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
          <p style={{ color: "#888" }}>暂无会话，点击新建开始</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {sessions.map((s) => (
            <div key={s.id} style={{ padding: 12, backgroundColor: "#111127", borderRadius: 6, border: "1px solid #1e1e3a", cursor: "pointer" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>{s.title}</span>
                  <span style={{ marginLeft: 8, fontSize: 10, padding: "1px 6px", borderRadius: 3, backgroundColor: `${statusColors[s.status]}20`, color: statusColors[s.status] }}>
                    {statusLabels[s.status]}
                  </span>
                </div>
                <span style={{ fontSize: 11, color: "#666" }}>{s.model}</span>
              </div>
              <div style={{ fontSize: 10, color: "#555", marginTop: 4 }}>{s.created}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: 32, display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
        <FeatureCard icon="🐳" title="Docker 沙箱" desc="每个会话独立容器" />
        <FeatureCard icon="🧠" title="多模型路由" desc="GPT-4o / DeepSeek / Qwen" />
        <FeatureCard icon="🔄" title="模式切换" desc="本地 ↔ 云端无缝交接" />
      </div>
    </div>
  );
}

function SettingsView({ config }: { config: AppConfig | null }) {
  return (
    <div style={{ flex: 1, overflow: "auto", padding: 24 }}>
      <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>设置</h2>
      <div style={{ display: "grid", gap: 16, maxWidth: 500 }}>
        <SettingGroup title="通用">
          <SettingRow label="API 地址" value={config?.api_url || "http://localhost:8000"} />
          <SettingRow label="语言" value={config?.language || "zh"} />
          <SettingRow label="主题" value={config?.theme || "dark"} />
        </SettingGroup>
        <SettingGroup title="模型">
          <SettingRow label="默认模型" value="auto (智能路由)" />
          <SettingRow label="备选模型" value="deepseek-v3, gpt-4o, qwen-72b" />
        </SettingGroup>
        <SettingGroup title="沙箱">
          <SettingRow label="平台" value="ubuntu-22.04" />
          <SettingRow label="CPU" value="4 cores" />
          <SettingRow label="内存" value="8 GB" />
          <SettingRow label="磁盘" value="50 GB" />
        </SettingGroup>
        <SettingGroup title="安全">
          <SettingRow label="RBAC" value="admin" />
          <SettingRow label="命令拦截" value="启用" />
          <SettingRow label="网络过滤" value="Allowlist" />
        </SettingGroup>
      </div>
    </div>
  );
}

function SettingGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ backgroundColor: "#111127", borderRadius: 8, border: "1px solid #1e1e3a", padding: 16 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, color: "#aaa" }}>{title}</h3>
      {children}
    </div>
  );
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 0", borderBottom: "1px solid #1e1e3a" }}>
      <span style={{ fontSize: 12, color: "#888" }}>{label}</span>
      <span style={{ fontSize: 12 }}>{value}</span>
    </div>
  );
}

function PlaceholderView({ title, desc, icon }: { title: string; desc: string; icon: string }) {
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>{icon}</div>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>{title}</h2>
      <p style={{ color: "#888", fontSize: 13 }}>{desc}</p>
    </div>
  );
}
