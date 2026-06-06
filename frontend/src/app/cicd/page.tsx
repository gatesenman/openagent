"use client";

import { useTranslations } from "next-intl";

export default function CICDPage() {
  const t = useTranslations("cicd");

  const pipelines = [
    {
      id: "pl-001",
      name: "openagent/main",
      provider: "GitHub Actions",
      lastRun: "2 分钟前",
      status: "success",
      branch: "main",
      duration: "3m 24s",
    },
    {
      id: "pl-002",
      name: "openagent/scaffold",
      provider: "GitHub Actions",
      lastRun: "15 分钟前",
      status: "running",
      branch: "scaffold",
      duration: "1m 12s",
    },
    {
      id: "pl-003",
      name: "openagent/feature-auth",
      provider: "GitLab CI",
      lastRun: "2 小时前",
      status: "failed",
      branch: "feature/auth",
      duration: "5m 01s",
    },
  ];

  const statusConfig: Record<string, { color: string; label: string }> = {
    success: { color: "bg-green-900/30 text-green-400", label: t("success") },
    running: { color: "bg-blue-900/30 text-blue-400", label: t("running") },
    failed: { color: "bg-red-900/30 text-red-400", label: t("failed") },
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90">
          {t("createPipeline")}
        </button>
      </div>

      <div className="space-y-4">
        {pipelines.map((pl) => {
          const sc = statusConfig[pl.status];
          return (
            <div
              key={pl.id}
              className="bg-[var(--bg-secondary)] rounded-lg p-5 border border-[var(--border)]"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-xl">
                    {pl.status === "success" ? "✅" : pl.status === "running" ? "🔄" : "❌"}
                  </span>
                  <div>
                    <h3 className="font-semibold">{pl.name}</h3>
                    <span className="text-xs text-[var(--text-secondary)]">{pl.provider}</span>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${sc.color}`}>{sc.label}</span>
              </div>
              <div className="flex items-center gap-6 text-sm text-[var(--text-secondary)]">
                <span>🌿 {pl.branch}</span>
                <span>⏱ {pl.duration}</span>
                <span>🕐 {pl.lastRun}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
