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
          <SidebarItem icon="💬" label="会话" active />
          <SidebarItem icon="📚" label="知识库" />
          <SidebarItem icon="📖" label="Playbooks" />
          <SidebarItem icon="📊" label="分析" />
          <SidebarItem icon="⚙️" label="设置" />
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
        <main
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: 40,
          }}
        >
          <div style={{ textAlign: "center", maxWidth: 500 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
              OpenAgent Desktop
            </h1>
            <p style={{ color: "#888", fontSize: 14, marginBottom: 24 }}>
              AI 驱动的全生命周期软件开发平台
              <br />
              所有开发操作在隔离虚拟环境中执行
            </p>

            <button
              style={{
                padding: "10px 24px",
                backgroundColor: "#3b82f6",
                color: "white",
                border: "none",
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              + 新建会话
            </button>

            <div
              style={{
                marginTop: 32,
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr",
                gap: 12,
                textAlign: "left",
              }}
            >
              <FeatureCard
                icon="🐳"
                title="Docker 沙箱"
                desc="每个会话独立容器"
              />
              <FeatureCard
                icon="🧠"
                title="多模型路由"
                desc="GPT-4o / DeepSeek / Qwen"
              />
              <FeatureCard
                icon="🔄"
                title="模式切换"
                desc="本地 ↔ 云端无缝交接"
              />
            </div>
          </div>
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
}: {
  icon: string;
  label: string;
  active?: boolean;
}) {
  return (
    <button
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

function FeatureCard({
  icon,
  title,
  desc,
}: {
  icon: string;
  title: string;
  desc: string;
}) {
  return (
    <div
      style={{
        padding: 12,
        backgroundColor: "#111127",
        borderRadius: 8,
        border: "1px solid #1e1e3a",
      }}
    >
      <div style={{ fontSize: 20, marginBottom: 4 }}>{icon}</div>
      <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 2 }}>{title}</div>
      <div style={{ fontSize: 11, color: "#666" }}>{desc}</div>
    </div>
  );
}
