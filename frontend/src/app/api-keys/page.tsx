"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface ServiceUser {
  id: string;
  name: string;
  description: string;
  api_key_prefix: string;
  permissions: string[];
  is_active: boolean;
  last_used_at: number | null;
}

export default function APIKeysPage() {
  const t = useTranslations("apikeys");
  const [users] = useState<ServiceUser[]>([
    { id: "1", name: "CI/CD Pipeline", description: "GitHub Actions 自动化", api_key_prefix: "oa_abc...xyz", permissions: ["read", "write", "execute"], is_active: true, last_used_at: Date.now() / 1000 - 3600 },
    { id: "2", name: "Monitoring Bot", description: "性能监控集成", api_key_prefix: "oa_def...uvw", permissions: ["read"], is_active: true, last_used_at: Date.now() / 1000 - 86400 },
    { id: "3", name: "Legacy Integration", description: "旧系统对接", api_key_prefix: "oa_ghi...rst", permissions: ["read", "write"], is_active: false, last_used_at: null },
  ]);
  const [showCreate, setShowCreate] = useState(false);

  const formatTime = (ts: number | null) => {
    if (!ts) return t("never");
    const diff = Math.floor(Date.now() / 1000 - ts);
    if (diff < 3600) return `${Math.floor(diff / 60)} ${t("minutesAgo")}`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} ${t("hoursAgo")}`;
    return `${Math.floor(diff / 86400)} ${t("daysAgo")}`;
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm"
        >
          {t("createUser")}
        </button>
      </div>

      {showCreate && (
        <div className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] mb-6">
          <div className="space-y-3">
            <input placeholder={t("userName")} className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded px-3 py-2 text-sm" />
            <input placeholder={t("userDescription")} className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded px-3 py-2 text-sm" />
            <div className="flex gap-3">
              <label className="flex items-center gap-1 text-sm">
                <input type="checkbox" defaultChecked /> read
              </label>
              <label className="flex items-center gap-1 text-sm">
                <input type="checkbox" defaultChecked /> write
              </label>
              <label className="flex items-center gap-1 text-sm">
                <input type="checkbox" /> execute
              </label>
              <label className="flex items-center gap-1 text-sm">
                <input type="checkbox" /> admin
              </label>
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-3">
            <button onClick={() => setShowCreate(false)} className="px-3 py-1.5 text-sm text-[var(--text-secondary)]">
              {t("cancel")}
            </button>
            <button className="px-3 py-1.5 bg-[var(--accent)] text-white rounded text-sm">
              {t("generate")}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {users.map((user) => (
          <div
            key={user.id}
            className={`bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] ${
              !user.is_active ? "opacity-60" : ""
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{user.name}</span>
                  {!user.is_active && (
                    <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">{t("disabled")}</span>
                  )}
                </div>
                <div className="text-sm text-[var(--text-secondary)] mt-0.5">{user.description}</div>
                <div className="flex items-center gap-3 mt-2">
                  <code className="text-xs bg-zinc-800 px-2 py-0.5 rounded font-mono">{user.api_key_prefix}</code>
                  <span className="text-xs text-[var(--text-secondary)]">
                    {t("lastUsed")}: {formatTime(user.last_used_at)}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {user.permissions.map((p) => (
                  <span key={p} className="text-xs bg-zinc-700 text-zinc-300 px-2 py-0.5 rounded-full">{p}</span>
                ))}
                <button className="ml-2 text-xs text-red-400 hover:text-red-300">{t("revoke")}</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
