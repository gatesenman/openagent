"use client";

import { useTranslations } from "next-intl";

export default function SchedulesPage() {
  const t = useTranslations("schedules");

  const schedules = [
    {
      id: "sched-001",
      name: "每日依赖更新",
      prompt: "更新所有依赖并运行测试",
      type: "cron",
      schedule: "0 9 * * *",
      status: "active",
      lastRun: "2026-06-06 09:00",
      nextRun: "2026-06-07 09:00",
    },
    {
      id: "sched-002",
      name: "每周安全扫描",
      prompt: "运行 OWASP 安全扫描并生成报告",
      type: "cron",
      schedule: "0 2 * * 1",
      status: "active",
      lastRun: "2026-06-02 02:00",
      nextRun: "2026-06-09 02:00",
    },
    {
      id: "sched-003",
      name: "代码质量检查",
      prompt: "运行 lint、类型检查和测试覆盖率",
      type: "interval",
      schedule: "每 6 小时",
      status: "paused",
      lastRun: "2026-06-05 18:00",
      nextRun: "-",
    },
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
        {schedules.map((sched) => (
          <div
            key={sched.id}
            className="bg-[var(--bg-secondary)] rounded-lg p-5 border border-[var(--border)]"
          >
            <div className="flex items-center justify-between mb-2">
              <div>
                <h3 className="font-semibold">{sched.name}</h3>
                <p className="text-xs text-[var(--text-secondary)] mt-1">{sched.prompt}</p>
              </div>
              <span
                className={`px-2 py-1 rounded text-xs ${
                  sched.status === "active"
                    ? "bg-green-900/30 text-green-400"
                    : "bg-gray-900/30 text-gray-400"
                }`}
              >
                {sched.status === "active" ? t("active") : t("paused")}
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-[var(--text-secondary)]">
              <span><svg className="w-3 h-3 inline mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>{sched.type === "cron" ? `cron: ${sched.schedule}` : sched.schedule}</span>
              <span><svg className="w-3 h-3 inline mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>{t("lastRun")}: {sched.lastRun}</span>
              <span><svg className="w-3 h-3 inline mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>{t("nextRun")}: {sched.nextRun}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
