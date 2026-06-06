"use client";

import React, { useState } from "react";

interface Member {
  id: string;
  display_name: string;
  email: string;
  role: "admin" | "member" | "viewer";
  teams: string[];
  is_active: boolean;
}

const MOCK_MEMBERS: Member[] = [
  {
    id: "1",
    display_name: "管理员",
    email: "admin@example.com",
    role: "admin",
    teams: ["核心团队"],
    is_active: true,
  },
  {
    id: "2",
    display_name: "开发者A",
    email: "dev-a@example.com",
    role: "member",
    teams: ["前端团队"],
    is_active: true,
  },
  {
    id: "3",
    display_name: "观察者B",
    email: "viewer-b@example.com",
    role: "viewer",
    teams: [],
    is_active: true,
  },
];

export default function MembershipPage() {
  const [members] = useState<Member[]>(MOCK_MEMBERS);
  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");

  const roleColors: Record<string, string> = {
    admin: "#ef4444",
    member: "#3b82f6",
    viewer: "#6b7280",
  };

  const roleLabels: Record<string, string> = {
    admin: "管理员",
    member: "成员",
    viewer: "观察者",
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
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>成员管理</h1>
          <p style={{ color: "#888", fontSize: 13 }}>
            管理组织成员和团队权限
          </p>
        </div>
        <button
          onClick={() => setShowInvite(!showInvite)}
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
          + 邀请成员
        </button>
      </div>

      {/* 邀请面板 */}
      {showInvite && (
        <div
          style={{
            padding: 16,
            backgroundColor: "#111827",
            borderRadius: 8,
            border: "1px solid #1f2937",
            marginBottom: 16,
            display: "flex",
            gap: 12,
            alignItems: "flex-end",
          }}
        >
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: 11, color: "#888", display: "block", marginBottom: 4 }}>
              邮箱
            </label>
            <input
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="user@example.com"
              style={{
                width: "100%",
                padding: "6px 10px",
                backgroundColor: "#0a0a1a",
                border: "1px solid #374151",
                borderRadius: 4,
                color: "white",
                fontSize: 13,
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: 11, color: "#888", display: "block", marginBottom: 4 }}>
              角色
            </label>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              style={{
                padding: "6px 10px",
                backgroundColor: "#0a0a1a",
                border: "1px solid #374151",
                borderRadius: 4,
                color: "white",
                fontSize: 13,
              }}
            >
              <option value="admin">管理员</option>
              <option value="member">成员</option>
              <option value="viewer">观察者</option>
            </select>
          </div>
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
            发送邀请
          </button>
        </div>
      )}

      {/* 成员列表 */}
      <div
        style={{
          backgroundColor: "#111827",
          borderRadius: 8,
          border: "1px solid #1f2937",
          overflow: "hidden",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #1f2937" }}>
              <th
                style={{
                  textAlign: "left",
                  padding: "10px 16px",
                  fontSize: 11,
                  color: "#888",
                  fontWeight: 500,
                }}
              >
                成员
              </th>
              <th style={{ textAlign: "left", padding: "10px 16px", fontSize: 11, color: "#888" }}>
                角色
              </th>
              <th style={{ textAlign: "left", padding: "10px 16px", fontSize: 11, color: "#888" }}>
                团队
              </th>
              <th style={{ textAlign: "right", padding: "10px 16px", fontSize: 11, color: "#888" }}>
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            {members.map((m) => (
              <tr
                key={m.id}
                style={{ borderBottom: "1px solid #1f2937" }}
              >
                <td style={{ padding: "10px 16px" }}>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>{m.display_name}</div>
                  <div style={{ fontSize: 11, color: "#666" }}>{m.email}</div>
                </td>
                <td style={{ padding: "10px 16px" }}>
                  <span
                    style={{
                      fontSize: 11,
                      padding: "2px 8px",
                      borderRadius: 4,
                      backgroundColor: `${roleColors[m.role]}20`,
                      color: roleColors[m.role],
                    }}
                  >
                    {roleLabels[m.role]}
                  </span>
                </td>
                <td style={{ padding: "10px 16px", fontSize: 12, color: "#888" }}>
                  {m.teams.length > 0 ? m.teams.join(", ") : "—"}
                </td>
                <td style={{ padding: "10px 16px", textAlign: "right" }}>
                  <button
                    style={{
                      padding: "4px 8px",
                      backgroundColor: "transparent",
                      border: "1px solid #374151",
                      borderRadius: 4,
                      color: "#888",
                      fontSize: 11,
                      cursor: "pointer",
                      marginRight: 4,
                    }}
                  >
                    编辑
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* RBAC 说明 */}
      <div
        style={{
          marginTop: 24,
          padding: 16,
          backgroundColor: "#111827",
          borderRadius: 8,
          border: "1px solid #1f2937",
        }}
      >
        <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>权限说明</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
          {[
            { role: "管理员", perms: "全部权限、成员管理、计费管理、组织设置" },
            { role: "成员", perms: "创建会话、编辑代码、提交PR、查看分析" },
            { role: "观察者", perms: "只读访问、查看会话日志、查看分析" },
          ].map((r) => (
            <div key={r.role}>
              <div style={{ fontSize: 12, fontWeight: 500, marginBottom: 4 }}>{r.role}</div>
              <div style={{ fontSize: 11, color: "#888" }}>{r.perms}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
