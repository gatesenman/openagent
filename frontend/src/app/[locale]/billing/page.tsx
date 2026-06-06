"use client";

import React, { useState } from "react";

interface PlanInfo {
  plan: string;
  label: string;
  price: string;
  acu: number;
  sessions: number;
  sandboxes: number;
  current: boolean;
}

const PLANS: PlanInfo[] = [
  { plan: "free", label: "Free", price: "¥0", acu: 50, sessions: 10, sandboxes: 1, current: true },
  { plan: "pro", label: "Pro", price: "¥99/月", acu: 500, sessions: 100, sandboxes: 5, current: false },
  { plan: "team", label: "Team", price: "¥399/月", acu: 2000, sessions: 500, sandboxes: 20, current: false },
  { plan: "enterprise", label: "Enterprise", price: "定制", acu: 999999, sessions: 999999, sandboxes: 100, current: false },
];

export default function BillingPage() {
  const [usedAcu] = useState(32.5);
  const [totalAcu] = useState(50);

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>计费管理</h1>
      <p style={{ color: "#888", fontSize: 13, marginBottom: 24 }}>
        ACU (Agent Compute Unit) 综合计费
      </p>

      {/* 用量概览 */}
      <div
        style={{
          padding: 20,
          backgroundColor: "#111827",
          borderRadius: 8,
          border: "1px solid #1f2937",
          marginBottom: 24,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
          <span style={{ fontSize: 14, fontWeight: 600 }}>本月用量</span>
          <span style={{ fontSize: 13, color: "#888" }}>
            {usedAcu} / {totalAcu} ACU
          </span>
        </div>
        <div
          style={{
            height: 8,
            backgroundColor: "#1f2937",
            borderRadius: 4,
            overflow: "hidden",
            marginBottom: 12,
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${(usedAcu / totalAcu) * 100}%`,
              backgroundColor: usedAcu / totalAcu > 0.8 ? "#f59e0b" : "#3b82f6",
              borderRadius: 4,
            }}
          />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 16 }}>
          {[
            { label: "总会话数", value: "24" },
            { label: "LLM Token", value: "1.2M" },
            { label: "沙箱时长", value: "8.5h" },
            { label: "预估费用", value: "¥0" },
          ].map((s) => (
            <div key={s.label}>
              <div style={{ fontSize: 18, fontWeight: 700 }}>{s.value}</div>
              <div style={{ fontSize: 11, color: "#666" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 计划列表 */}
      <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>计划</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 12 }}>
        {PLANS.map((p) => (
          <div
            key={p.plan}
            style={{
              padding: 16,
              backgroundColor: "#111827",
              borderRadius: 8,
              border: p.current ? "2px solid #3b82f6" : "1px solid #1f2937",
              textAlign: "center",
            }}
          >
            {p.current && (
              <div
                style={{
                  fontSize: 10,
                  color: "#3b82f6",
                  marginBottom: 8,
                  fontWeight: 600,
                }}
              >
                当前计划
              </div>
            )}
            <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>{p.label}</div>
            <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: "#3b82f6" }}>
              {p.price}
            </div>
            <div style={{ fontSize: 11, color: "#888", lineHeight: 1.8 }}>
              <div>{p.acu >= 999999 ? "无限" : p.acu} ACU/月</div>
              <div>{p.sessions >= 999999 ? "无限" : p.sessions} 会话</div>
              <div>{p.sandboxes} 并发沙箱</div>
            </div>
            {!p.current && (
              <button
                style={{
                  marginTop: 12,
                  padding: "6px 16px",
                  backgroundColor: "transparent",
                  border: "1px solid #374151",
                  borderRadius: 4,
                  color: "#888",
                  fontSize: 12,
                  cursor: "pointer",
                }}
              >
                升级
              </button>
            )}
          </div>
        ))}
      </div>

      {/* ACU 说明 */}
      <div
        style={{
          marginTop: 24,
          padding: 16,
          backgroundColor: "#111827",
          borderRadius: 8,
          border: "1px solid #1f2937",
        }}
      >
        <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>ACU 计费说明</h3>
        <div style={{ fontSize: 12, color: "#888", lineHeight: 1.8 }}>
          <div>XS 会话 (&lt;5分钟): 1 ACU</div>
          <div>S 会话 (5-15分钟): 5 ACU</div>
          <div>M 会话 (15-60分钟): 20 ACU</div>
          <div>L 会话 (1-4小时): 80 ACU</div>
          <div>XL 会话 (&gt;4小时): 200 ACU</div>
          <div style={{ marginTop: 4, color: "#666" }}>+ LLM Token: 每 1M token = 1 ACU</div>
        </div>
      </div>
    </div>
  );
}
