"use client";

import React, { useState } from "react";

interface Pipeline {
  id: string;
  branch: string;
  commit: string;
  status: "pending" | "running" | "success" | "failure";
  provider: string;
  steps: { name: string; status: string; duration: string }[];
  triggered_at: string;
}

const MOCK: Pipeline[] = [
  {
    id: "p1",
    branch: "main",
    commit: "a1b2c3d",
    status: "success",
    provider: "github_actions",
    steps: [
      { name: "lint", status: "success", duration: "12s" },
      { name: "typecheck", status: "success", duration: "8s" },
      { name: "test", status: "success", duration: "45s" },
      { name: "build", status: "success", duration: "30s" },
    ],
    triggered_at: "2026-06-06 15:30",
  },
  {
    id: "p2",
    branch: "feat/auth",
    commit: "e4f5g6h",
    status: "failure",
    provider: "github_actions",
    steps: [
      { name: "lint", status: "success", duration: "11s" },
      { name: "typecheck", status: "failure", duration: "6s" },
      { name: "test", status: "pending", duration: "-" },
      { name: "build", status: "pending", duration: "-" },
    ],
    triggered_at: "2026-06-06 14:15",
  },
];

export default function CICDPage() {
  const [pipelines] = useState<Pipeline[]>(MOCK);

  const statusColors: Record<string, string> = {
    pending: "#6b7280",
    running: "#3b82f6",
    success: "#10b981",
    failure: "#ef4444",
  };
  const statusLabels: Record<string, string> = {
    pending: "等待中",
    running: "运行中",
    success: "成功",
    failure: "失败",
  };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>CI/CD 流水线</h1>
          <p style={{ color: "#888", fontSize: 13 }}>管理构建、测试和部署流水线</p>
        </div>
        <button style={{ padding: "8px 16px", backgroundColor: "#3b82f6", color: "white", border: "none", borderRadius: 6, fontSize: 13, cursor: "pointer" }}>
          + 触发构建
        </button>
      </div>

      {pipelines.map((p) => (
        <div key={p.id} style={{ marginBottom: 16, padding: 16, backgroundColor: "#111827", borderRadius: 8, border: "1px solid #1f2937" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
            <div>
              <span style={{ fontSize: 14, fontWeight: 600 }}>{p.branch}</span>
              <span style={{ marginLeft: 8, fontSize: 11, color: "#666", fontFamily: "monospace" }}>{p.commit}</span>
              <span style={{ marginLeft: 8, fontSize: 11, padding: "2px 8px", borderRadius: 4, backgroundColor: `${statusColors[p.status]}20`, color: statusColors[p.status] }}>
                {statusLabels[p.status]}
              </span>
            </div>
            <span style={{ fontSize: 11, color: "#666" }}>{p.triggered_at}</span>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {p.steps.map((s, i) => (
              <div key={i} style={{ flex: 1, padding: "8px 12px", backgroundColor: "#0a0a1a", borderRadius: 4, border: `1px solid ${statusColors[s.status]}40` }}>
                <div style={{ fontSize: 12, fontWeight: 500, marginBottom: 4 }}>{s.name}</div>
                <div style={{ fontSize: 11, color: statusColors[s.status] }}>{statusLabels[s.status]}</div>
                <div style={{ fontSize: 10, color: "#666", marginTop: 2 }}>{s.duration}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
