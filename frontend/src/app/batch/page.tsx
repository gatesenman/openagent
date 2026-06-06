"use client";

import { useTranslations } from "next-intl";

export default function BatchSessionsPage() {
  const t = useTranslations("batch");

  const batches = [
    { id: "batch-001", name: "重构 API 层", total: 5, completed: 3, status: "running" },
    { id: "batch-002", name: "修复安全漏洞", total: 8, completed: 8, status: "completed" },
    { id: "batch-003", name: "添加单元测试", total: 12, completed: 0, status: "pending" },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90">
          {t("create")}
        </button>
      </div>

      <div className="space-y-4">
        {batches.map((batch) => (
          <div
            key={batch.id}
            className="bg-[var(--bg-secondary)] rounded-lg p-5 border border-[var(--border)]"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-lg">{batch.name}</h3>
              <span
                className={`px-2 py-1 rounded text-xs ${
                  batch.status === "completed"
                    ? "bg-green-900/30 text-green-400"
                    : batch.status === "running"
                    ? "bg-blue-900/30 text-blue-400"
                    : "bg-gray-900/30 text-gray-400"
                }`}
              >
                {batch.status === "completed" ? t("completed") : batch.status === "running" ? t("running") : t("pending")}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1 h-2 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[var(--accent)] rounded-full transition-all"
                  style={{ width: `${(batch.completed / batch.total) * 100}%` }}
                />
              </div>
              <span className="text-sm text-[var(--text-secondary)]">
                {batch.completed}/{batch.total} {t("tasks")}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
