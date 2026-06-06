"use client";

import React, { useState } from "react";

interface SnapshotItem {
  id: string;
  name: string;
  status: "ready" | "building" | "failed";
  platform: string;
  size: string;
  built_at: string;
}

const MOCK: SnapshotItem[] = [
  { id: "s1", name: "ubuntu-base-20260606", status: "ready", platform: "ubuntu-22.04", size: "2.1 GB", built_at: "2026-06-06 14:00" },
  { id: "s2", name: "node18-python312", status: "ready", platform: "ubuntu-22.04", size: "3.4 GB", built_at: "2026-06-05 10:30" },
  { id: "s3", name: "fullstack-dev", status: "building", platform: "ubuntu-22.04", size: "-", built_at: "-" },
];

export default function SnapshotsPage() {
  const [snapshots] = useState<SnapshotItem[]>(MOCK);

  const statusColors: Record<string, string> = { ready: "#10b981", building: "#3b82f6", failed: "#ef4444" };
  const statusLabels: Record<string, string> = { ready: "就绪", building: "构建中", failed: "失败" };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>环境快照</h1>
          <p style={{ color: "#888", fontSize: 13 }}>管理 Devbox 环境快照，加速会话启动</p>
        </div>
        <button style={{ padding: "8px 16px", backgroundColor: "#3b82f6", color: "white", border: "none", borderRadius: 6, fontSize: 13, cursor: "pointer" }}>
          + 构建快照
        </button>
      </div>

      <div style={{ backgroundColor: "#111827", borderRadius: 8, border: "1px solid #1f2937", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #1f2937" }}>
              <th style={{ textAlign: "left", padding: "10px 16px", fontSize: 11, color: "#888" }}>名称</th>
              <th style={{ textAlign: "left", padding: "10px 16px", fontSize: 11, color: "#888" }}>状态</th>
              <th style={{ textAlign: "left", padding: "10px 16px", fontSize: 11, color: "#888" }}>平台</th>
              <th style={{ textAlign: "left", padding: "10px 16px", fontSize: 11, color: "#888" }}>大小</th>
              <th style={{ textAlign: "left", padding: "10px 16px", fontSize: 11, color: "#888" }}>构建时间</th>
              <th style={{ textAlign: "right", padding: "10px 16px", fontSize: 11, color: "#888" }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {snapshots.map((s) => (
              <tr key={s.id} style={{ borderBottom: "1px solid #1f2937" }}>
                <td style={{ padding: "10px 16px", fontSize: 13 }}>{s.name}</td>
                <td style={{ padding: "10px 16px" }}>
                  <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 4, backgroundColor: `${statusColors[s.status]}20`, color: statusColors[s.status] }}>
                    {statusLabels[s.status]}
                  </span>
                </td>
                <td style={{ padding: "10px 16px", fontSize: 12, color: "#888" }}>{s.platform}</td>
                <td style={{ padding: "10px 16px", fontSize: 12, color: "#888" }}>{s.size}</td>
                <td style={{ padding: "10px 16px", fontSize: 12, color: "#888" }}>{s.built_at}</td>
                <td style={{ padding: "10px 16px", textAlign: "right" }}>
                  <button style={{ padding: "4px 8px", backgroundColor: "transparent", border: "1px solid #374151", borderRadius: 4, color: "#888", fontSize: 11, cursor: "pointer", marginRight: 4 }}>恢复</button>
                  <button style={{ padding: "4px 8px", backgroundColor: "transparent", border: "1px solid #374151", borderRadius: 4, color: "#888", fontSize: 11, cursor: "pointer" }}>删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
