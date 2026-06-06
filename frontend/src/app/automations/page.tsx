"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface AutomationRule {
  id: string;
  name: string;
  trigger_type: string;
  trigger_config: Record<string, string>;
  action: string;
  enabled: boolean;
}

export default function AutomationsPage() {
  const t = useTranslations("automations");
  const [rules] = useState<AutomationRule[]>([
    { id: "1", name: "PR 自动 Review", trigger_type: "pr_opened", trigger_config: { repo: "*" }, action: "auto_review", enabled: true },
    { id: "2", name: "每日代码扫描", trigger_type: "schedule", trigger_config: { cron: "0 9 * * *" }, action: "code_scan", enabled: true },
    { id: "3", name: "Issue 自动分析", trigger_type: "issue_created", trigger_config: { labels: "bug" }, action: "analyze_issue", enabled: false },
    { id: "4", name: "Webhook 部署通知", trigger_type: "webhook", trigger_config: { url: "/hooks/deploy" }, action: "notify_deploy", enabled: true },
  ]);

  const triggerIcons: Record<string, string> = {
    pr_opened: "🔀",
    schedule: "⏰",
    issue_created: "🐛",
    webhook: "🔗",
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm">
          {t("createRule")}
        </button>
      </div>

      <div className="space-y-3">
        {rules.map((rule) => (
          <div
            key={rule.id}
            className={`bg-[var(--bg-secondary)] rounded-lg p-4 border transition ${
              rule.enabled ? "border-[var(--border)]" : "border-[var(--border)] opacity-60"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-xl">{triggerIcons[rule.trigger_type] || "⚡"}</span>
                <div>
                  <div className="font-medium">{rule.name}</div>
                  <div className="text-xs text-[var(--text-secondary)] mt-0.5">
                    {t("trigger")}: {rule.trigger_type} | {t("action")}: {rule.action}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button
                  className={`w-10 h-5 rounded-full transition relative ${
                    rule.enabled ? "bg-[var(--accent)]" : "bg-zinc-600"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition ${
                      rule.enabled ? "left-5" : "left-0.5"
                    }`}
                  />
                </button>
                <button className="text-xs text-[var(--text-secondary)] hover:text-white">
                  {t("edit")}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
