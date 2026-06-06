"use client";

import { useTranslations } from "next-intl";

export default function AnalyticsPage() {
  const t = useTranslations("analytics");

  const stats = [
    {
      label: t("llmCalls"),
      value: "1,284",
      change: "+12%",
      icon: "🤖",
    },
    {
      label: t("toolCalls"),
      value: "3,456",
      change: "+8%",
      icon: "🔧",
    },
    {
      label: t("sessions"),
      value: "89",
      change: "+23%",
      icon: "📊",
    },
    {
      label: t("sandbox"),
      value: "42",
      change: "+5%",
      icon: "📦",
    },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{t("title")}</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)]"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{stat.icon}</span>
              <span className="text-xs text-green-400">{stat.change}</span>
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm text-[var(--text-secondary)]">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* LLM 使用明细 */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)] mb-6">
        <h2 className="text-lg font-semibold mb-4">LLM 调用明细</h2>
        <div className="space-y-3">
          {[
            { model: "GPT-4o", calls: 456, tokens: "2.3M", cost: "$34.50" },
            { model: "DeepSeek-V3", calls: 328, tokens: "1.8M", cost: "$5.40" },
            { model: "Qwen-Max", calls: 245, tokens: "1.2M", cost: "$3.60" },
            { model: "Claude 4 Sonnet", calls: 189, tokens: "980K", cost: "$14.70" },
            { model: "Llama 3.3", calls: 66, tokens: "450K", cost: "$0.00" },
          ].map((row) => (
            <div
              key={row.model}
              className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0"
            >
              <span className="font-medium">{row.model}</span>
              <div className="flex gap-6 text-sm text-[var(--text-secondary)]">
                <span>{row.calls} 次</span>
                <span>{row.tokens} tokens</span>
                <span className="text-[var(--accent)]">{row.cost}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 工具调用排行 */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)]">
        <h2 className="text-lg font-semibold mb-4">工具调用排行</h2>
        <div className="space-y-2">
          {[
            { tool: "shell_exec", count: 1234, rate: "98.2%" },
            { tool: "file_write", count: 890, rate: "99.5%" },
            { tool: "file_read", count: 756, rate: "100%" },
            { tool: "search_code", count: 432, rate: "97.8%" },
            { tool: "git_ops", count: 144, rate: "99.3%" },
          ].map((row) => (
            <div key={row.tool} className="flex items-center gap-3">
              <span className="font-mono text-sm w-28">{row.tool}</span>
              <div className="flex-1 h-2 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[var(--accent)] rounded-full"
                  style={{ width: `${(row.count / 1234) * 100}%` }}
                />
              </div>
              <span className="text-sm text-[var(--text-secondary)] w-16 text-right">
                {row.count}
              </span>
              <span className="text-xs text-green-400 w-14 text-right">
                {row.rate}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
