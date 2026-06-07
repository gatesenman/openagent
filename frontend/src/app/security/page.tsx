"use client";

import { useTranslations } from "next-intl";

export default function SecurityPage() {
  const t = useTranslations("security");

  const owaspRules = [
    {
      id: "LLM01",
      name: "Prompt Injection",
      risk: "critical",
      status: "active",
      patterns: 6,
    },
    {
      id: "LLM02",
      name: "Insecure Output Handling",
      risk: "high",
      status: "active",
      patterns: 5,
    },
    {
      id: "LLM03",
      name: "Training Data Poisoning",
      risk: "medium",
      status: "monitoring",
      patterns: 0,
    },
    {
      id: "LLM04",
      name: "Model Denial of Service",
      risk: "medium",
      status: "active",
      patterns: 3,
    },
    {
      id: "LLM05",
      name: "Supply Chain Vulnerabilities",
      risk: "high",
      status: "monitoring",
      patterns: 0,
    },
    {
      id: "LLM06",
      name: "Sensitive Info Disclosure",
      risk: "high",
      status: "active",
      patterns: 4,
    },
    {
      id: "LLM07",
      name: "System Prompt Leakage",
      risk: "medium",
      status: "active",
      patterns: 3,
    },
    {
      id: "LLM08",
      name: "Vector / Embedding Weakness",
      risk: "low",
      status: "planned",
      patterns: 0,
    },
    {
      id: "LLM09",
      name: "Misinformation",
      risk: "medium",
      status: "active",
      patterns: 2,
    },
    {
      id: "LLM10",
      name: "Unbounded Consumption",
      risk: "medium",
      status: "active",
      patterns: 2,
    },
  ];

  const riskColors: Record<string, string> = {
    critical: "bg-red-500/20 text-red-400",
    high: "bg-orange-500/20 text-orange-400",
    medium: "bg-yellow-500/20 text-yellow-400",
    low: "bg-green-500/20 text-green-400",
  };

  const statusColors: Record<string, string> = {
    active: "bg-green-500/20 text-green-400",
    monitoring: "bg-blue-500/20 text-blue-400",
    planned: "bg-gray-500/20 text-gray-400",
  };

  const securityStats = [
    { label: t("blockedInjections"), value: "342", icon: "🛡️" },
    { label: t("commandsChecked"), value: "8,921", icon: "🔍" },
    { label: t("sensitiveFilesBlocked"), value: "56", icon: "🔒" },
    { label: t("riskScore"), value: "96.8", icon: "📊" },
  ];

  const dangerousCommands = [
    { pattern: "rm -rf /", blocked: 12, last: "2h ago" },
    { pattern: "DROP TABLE", blocked: 5, last: "1d ago" },
    { pattern: "curl | bash", blocked: 8, last: "4h ago" },
    { pattern: "chmod -R 777 /", blocked: 3, last: "3d ago" },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">{t("title")}</h1>
      <p className="text-[var(--text-secondary)] mb-6">{t("subtitle")}</p>

      {/* 安全统计 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {securityStats.map((stat) => (
          <div
            key={stat.label}
            className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)]"
          >
            <div className="text-2xl mb-1">{stat.icon}</div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm text-[var(--text-secondary)]">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* OWASP LLM Top 10 */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)] mb-6">
        <h2 className="text-lg font-semibold mb-4">OWASP LLM Top 10 (2025)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[var(--text-secondary)] border-b border-[var(--border)]">
                <th className="py-2 pr-4">ID</th>
                <th className="py-2 pr-4">{t("ruleName")}</th>
                <th className="py-2 pr-4">{t("riskLevel")}</th>
                <th className="py-2 pr-4">{t("status")}</th>
                <th className="py-2 text-right">{t("patterns")}</th>
              </tr>
            </thead>
            <tbody>
              {owaspRules.map((rule) => (
                <tr key={rule.id} className="border-b border-[var(--border)] last:border-0">
                  <td className="py-2.5 pr-4 font-mono text-[var(--accent)]">{rule.id}</td>
                  <td className="py-2.5 pr-4 font-medium">{rule.name}</td>
                  <td className="py-2.5 pr-4">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${riskColors[rule.risk]}`}>
                      {rule.risk.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-2.5 pr-4">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${statusColors[rule.status]}`}>
                      {rule.status}
                    </span>
                  </td>
                  <td className="py-2.5 text-right">{rule.patterns}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 危险命令拦截 */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)]">
        <h2 className="text-lg font-semibold mb-4">{t("dangerousCommands")}</h2>
        <div className="space-y-2">
          {dangerousCommands.map((cmd) => (
            <div
              key={cmd.pattern}
              className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0"
            >
              <code className="text-sm font-mono text-red-400 bg-red-500/10 px-2 py-0.5 rounded">
                {cmd.pattern}
              </code>
              <div className="flex gap-6 text-sm text-[var(--text-secondary)]">
                <span>{t("blocked")}: {cmd.blocked}</span>
                <span>{cmd.last}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
