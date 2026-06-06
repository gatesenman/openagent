"use client";

import React, { useState } from "react";

interface BatchItem {
  id: string;
  title: string;
  status: "pending" | "running" | "completed" | "partial" | "failed";
  subtask_count: number;
  completed_count: number;
  created_at: string;
}

const MOCK_BATCHES: BatchItem[] = [
  {
    id: "b1",
    title: "重构认证模块",
    status: "completed",
    subtask_count: 4,
    completed_count: 4,
    created_at: "2026-06-06",
  },
  {
    id: "b2",
    title: "多语言国际化",
    status: "running",
    subtask_count: 6,
    completed_count: 3,
    created_at: "2026-06-06",
  },
  {
    id: "b3",
    title: "API 端点测试",
    status: "pending",
    subtask_count: 10,
    completed_count: 0,
    created_at: "2026-06-06",
  },
];

export default function BatchPage() {
  const [batches] = useState<BatchItem[]>(MOCK_BATCHES);
  const [showCreate, setShowCreate] = useState(false);

  const statusColors: Record<string, string> = {
    pending: "#6b7280",
    running: "#3b82f6",
    completed: "#10b981",
    partial: "#f59e0b",
    failed: "#ef4444",
  };

  const statusLabels: Record<string, string> = {
    pending: "待执行",
    running: "运行中",
    completed: "已完成",
    partial: "部分完成",
    failed: "失败",
  };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24,
        }}
      >
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>批量会话</h1>
          <p style={{ color: "#888", fontSize: 13 }}>
            将大任务拆分为子任务，多个 Agent 并行执行
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          style={{
            padding: "8px 16px",
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: 6,
            fontSize: 13,
            cursor: "pointer",
          }}
        >
          + 创建批量任务
        </button>
      </div>

      {/* 创建面板 */}
      {showCreate && (
        <div
          style={{
            padding: 16,
            backgroundColor: "#111827",
            borderRadius: 8,
            border: "1px solid #1f2937",
            marginBottom: 16,
          }}
        >
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 11, color: "#888", display: "block", marginBottom: 4 }}>
              任务描述
            </label>
            <textarea
              placeholder="描述你要完成的大任务，Agent 会自动拆分为子任务..."
              style={{
                width: "100%",
                padding: "8px 10px",
                backgroundColor: "#0a0a1a",
                border: "1px solid #374151",
                borderRadius: 4,
                color: "white",
                fontSize: 13,
                minHeight: 80,
                resize: "vertical",
              }}
            />
          </div>
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <select
              style={{
                padding: "6px 10px",
                backgroundColor: "#0a0a1a",
                border: "1px solid #374151",
                borderRadius: 4,
                color: "white",
                fontSize: 13,
              }}
            >
              <option value="auto">自动合并</option>
              <option value="sequential">顺序执行</option>
              <option value="manual">手动合并</option>
            </select>
            <button
              style={{
                padding: "6px 16px",
                backgroundColor: "#10b981",
                color: "white",
                border: "none",
                borderRadius: 4,
                fontSize: 13,
                cursor: "pointer",
              }}
            >
              创建并启动
            </button>
          </div>
        </div>
      )}

      {/* 批量任务列表 */}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {batches.map((b) => (
          <div
            key={b.id}
            style={{
              padding: 16,
              backgroundColor: "#111827",
              borderRadius: 8,
              border: "1px solid #1f2937",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 12,
              }}
            >
              <div>
                <span style={{ fontSize: 14, fontWeight: 600 }}>{b.title}</span>
                <span
                  style={{
                    marginLeft: 8,
                    fontSize: 11,
                    padding: "2px 8px",
                    borderRadius: 4,
                    backgroundColor: `${statusColors[b.status]}20`,
                    color: statusColors[b.status],
                  }}
                >
                  {statusLabels[b.status]}
                </span>
              </div>
              <span style={{ fontSize: 11, color: "#666" }}>{b.created_at}</span>
            </div>

            {/* 进度条 */}
            <div
              style={{
                height: 6,
                backgroundColor: "#1f2937",
                borderRadius: 3,
                marginBottom: 8,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${(b.completed_count / b.subtask_count) * 100}%`,
                  backgroundColor: statusColors[b.status],
                  borderRadius: 3,
                  transition: "width 0.3s",
                }}
              />
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#888" }}>
              <span>
                {b.completed_count} / {b.subtask_count} 子任务完成
              </span>
              <span>{Math.round((b.completed_count / b.subtask_count) * 100)}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
