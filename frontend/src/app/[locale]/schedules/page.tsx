"use client";

import React, { useState } from "react";

interface ScheduleItem {
  id: string;
  name: string;
  type: "cron" | "once" | "interval";
  expression: string;
  status: "active" | "paused";
  total_runs: number;
  last_run: string;
}

const MOCK: ScheduleItem[] = [
  { id: "sc1", name: "每日依赖更新", type: "cron", expression: "0 9 * * *", status: "active", total_runs: 15, last_run: "2026-06-06 09:00" },
  { id: "sc2", name: "周五安全扫描", type: "cron", expression: "0 18 * * 5", status: "active", total_runs: 4, last_run: "2026-05-31 18:00" },
  { id: "sc3", name: "一次性迁移", type: "once", expression: "2026-06-10 10:00", status: "paused", total_runs: 0, last_run: "-" },
];

export default function SchedulesPage() {
  const [schedules] = useState<ScheduleItem[]>(MOCK);
  const [showCreate, setShowCreate] = useState(false);

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>调度管理</h1>
          <p style={{ color: "#888", fontSize: 13 }}>配置定时任务和一次性会话调度</p>
        </div>
        <button onClick={() => setShowCreate(!showCreate)} style={{ padding: "8px 16px", backgroundColor: "#3b82f6", color: "white", border: "none", borderRadius: 6, fontSize: 13, cursor: "pointer" }}>
          + 创建调度
        </button>
      </div>

      {showCreate && (
        <div style={{ padding: 16, backgroundColor: "#111827", borderRadius: 8, border: "1px solid #1f2937", marginBottom: 16 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
            <div>
              <label style={{ fontSize: 11, color: "#888", display: "block", marginBottom: 4 }}>名称</label>
              <input placeholder="调度名称" style={{ width: "100%", padding: "6px 10px", backgroundColor: "#0a0a1a", border: "1px solid #374151", borderRadius: 4, color: "white", fontSize: 13 }} />
            </div>
            <div>
              <label style={{ fontSize: 11, color: "#888", display: "block", marginBottom: 4 }}>类型</label>
              <select style={{ width: "100%", padding: "6px 10px", backgroundColor: "#0a0a1a", border: "1px solid #374151", borderRadius: 4, color: "white", fontSize: 13 }}>
                <option value="cron">Cron 定时</option>
                <option value="interval">固定间隔</option>
                <option value="once">一次性</option>
              </select>
            </div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 11, color: "#888", display: "block", marginBottom: 4 }}>任务描述</label>
            <textarea placeholder="Agent 要执行的任务..." style={{ width: "100%", padding: "8px 10px", backgroundColor: "#0a0a1a", border: "1px solid #374151", borderRadius: 4, color: "white", fontSize: 13, minHeight: 60, resize: "vertical" }} />
          </div>
          <button style={{ padding: "6px 16px", backgroundColor: "#10b981", color: "white", border: "none", borderRadius: 4, fontSize: 13, cursor: "pointer" }}>创建</button>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {schedules.map((s) => (
          <div key={s.id} style={{ padding: 16, backgroundColor: "#111827", borderRadius: 8, border: "1px solid #1f2937", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
                {s.name}
                <span style={{ marginLeft: 8, fontSize: 11, padding: "2px 8px", borderRadius: 4, backgroundColor: s.status === "active" ? "#10b98120" : "#6b728020", color: s.status === "active" ? "#10b981" : "#6b7280" }}>
                  {s.status === "active" ? "运行中" : "已暂停"}
                </span>
              </div>
              <div style={{ fontSize: 12, color: "#888" }}>
                <span style={{ fontFamily: "monospace" }}>{s.expression}</span>
                <span style={{ margin: "0 8px" }}>|</span>
                已执行 {s.total_runs} 次
                <span style={{ margin: "0 8px" }}>|</span>
                上次: {s.last_run}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button style={{ padding: "4px 12px", backgroundColor: "transparent", border: "1px solid #374151", borderRadius: 4, color: "#888", fontSize: 11, cursor: "pointer" }}>
                {s.status === "active" ? "暂停" : "恢复"}
              </button>
              <button style={{ padding: "4px 12px", backgroundColor: "#3b82f620", border: "1px solid #3b82f640", borderRadius: 4, color: "#3b82f6", fontSize: 11, cursor: "pointer" }}>
                立即执行
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
