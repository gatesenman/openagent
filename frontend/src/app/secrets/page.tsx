"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface Secret {
  id: string;
  name: string;
  scope: string;
  created_by: string;
  repo_name: string | null;
}

export default function SecretsPage() {
  const t = useTranslations("secrets");
  const [secrets, setSecrets] = useState<Secret[]>([
    { id: "1", name: "OPENAI_API_KEY", scope: "org", created_by: "admin", repo_name: null },
    { id: "2", name: "DEEPSEEK_API_KEY", scope: "org", created_by: "admin", repo_name: null },
    { id: "3", name: "GITHUB_TOKEN", scope: "user", created_by: "user1", repo_name: null },
    { id: "4", name: "DB_PASSWORD", scope: "repo", created_by: "admin", repo_name: "openagent" },
  ]);
  const [showCreate, setShowCreate] = useState(false);

  const scopeColors: Record<string, string> = {
    org: "bg-blue-500/20 text-blue-400",
    user: "bg-green-500/20 text-green-400",
    repo: "bg-purple-500/20 text-purple-400",
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm hover:opacity-90"
        >
          {t("create")}
        </button>
      </div>

      <p className="text-sm text-[var(--text-secondary)] mb-6">{t("description")}</p>

      {showCreate && (
        <div className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] mb-6">
          <div className="grid grid-cols-2 gap-4">
            <input placeholder={t("name")} className="bg-[var(--bg-primary)] border border-[var(--border)] rounded px-3 py-2 text-sm" />
            <select className="bg-[var(--bg-primary)] border border-[var(--border)] rounded px-3 py-2 text-sm">
              <option value="org">{t("scopeOrg")}</option>
              <option value="user">{t("scopeUser")}</option>
              <option value="repo">{t("scopeRepo")}</option>
            </select>
            <input placeholder={t("value")} type="password" className="bg-[var(--bg-primary)] border border-[var(--border)] rounded px-3 py-2 text-sm col-span-2" />
          </div>
          <div className="flex justify-end gap-2 mt-3">
            <button onClick={() => setShowCreate(false)} className="px-3 py-1.5 text-sm text-[var(--text-secondary)] hover:text-white">
              {t("cancel")}
            </button>
            <button className="px-3 py-1.5 bg-[var(--accent)] text-white rounded text-sm">
              {t("save")}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {secrets.map((secret) => (
          <div
            key={secret.id}
            className="flex items-center justify-between bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)]"
          >
            <div className="flex items-center gap-3">
              <span className="text-lg">🔑</span>
              <div>
                <div className="font-mono text-sm font-medium">{secret.name}</div>
                {secret.repo_name && (
                  <div className="text-xs text-[var(--text-secondary)]">
                    {secret.repo_name}
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-2 py-0.5 rounded-full text-xs ${scopeColors[secret.scope] || ""}`}>
                {secret.scope}
              </span>
              <button className="text-red-400 hover:text-red-300 text-sm">{t("delete")}</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
