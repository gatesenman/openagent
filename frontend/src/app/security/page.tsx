"use client";

import { useTranslations } from "next-intl";

export default function SecurityPage() {
  const t = useTranslations("security");

  const owaspRules = [
    { id: "LLM01", name: "Prompt Injection", risk: "critical", status: "active", patterns: 6 },
    { id: "LLM02", name: "Insecure Output Handling", risk: "high", status: "active", patterns: 5 },
    { id: "LLM03", name: "Training Data Poisoning", risk: "medium", status: "monitoring", patterns: 0 },
    { id: "LLM04", name: "Model Denial of Service", risk: "medium", status: "active", patterns: 3 },
    { id: "LLM05", name: "Supply Chain Vulnerabilities", risk: "high", status: "active", patterns: 5 },
    { id: "LLM06", name: "Sensitive Info Disclosure", risk: "high", status: "active", patterns: 4 },
    { id: "LLM07", name: "System Prompt Leakage", risk: "medium", status: "active", patterns: 3 },
    { id: "LLM08", name: "Vector / Embedding Weakness", risk: "low", status: "planned", patterns: 0 },
    { id: "LLM09", name: "Misinformation", risk: "medium", status: "active", patterns: 2 },
    { id: "LLM10", name: "Unbounded Consumption", risk: "medium", status: "active", patterns: 2 },
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

  /* Codex Security — enterprise scan capabilities */
  const codexCapabilities = [
    {
      name: "SAST",
      fullName: "Static Application Security Testing",
      rules: 12,
      cwes: 12,
      languages: "Python, JS, TS, Java, Go, PHP",
      color: "text-purple-400",
    },
    {
      name: "SCA",
      fullName: "Software Composition Analysis",
      rules: 5,
      cwes: 0,
      languages: "PyPI, npm, Maven, Go, Cargo",
      color: "text-blue-400",
    },
    {
      name: "Secret Detection",
      fullName: "Hardcoded Secret Scanner",
      rules: 17,
      cwes: 1,
      languages: "AWS, GitHub, Stripe, OpenAI, Anthropic, ...",
      color: "text-red-400",
    },
    {
      name: "License Compliance",
      fullName: "Open Source License Checker",
      rules: 14,
      cwes: 0,
      languages: "MIT, Apache, GPL, AGPL, SSPL, ...",
      color: "text-yellow-400",
    },
    {
      name: "IaC Security",
      fullName: "Infrastructure as Code Scanner",
      rules: 7,
      cwes: 3,
      languages: "Docker, Kubernetes, Terraform",
      color: "text-cyan-400",
    },
    {
      name: "SBOM",
      fullName: "Software Bill of Materials",
      rules: 0,
      cwes: 0,
      languages: "CycloneDX 1.5",
      color: "text-green-400",
    },
  ];

  const complianceFrameworks = [
    { name: "SOC 2", controls: 7, passRate: 85, status: "active" },
    { name: "ISO 27001", controls: 5, passRate: 80, status: "active" },
    { name: "GDPR", controls: 3, passRate: 100, status: "active" },
    { name: "HIPAA", controls: 3, passRate: 67, status: "active" },
    { name: "PCI DSS", controls: 5, passRate: 0, status: "planned" },
    { name: "NIST 800-53", controls: 6, passRate: 0, status: "planned" },
  ];

  const policyRules = [
    { id: "POL-001", name: "Block Critical Vulnerabilities", action: "BLOCK", enabled: true },
    { id: "POL-002", name: "Require Secret Scanning", action: "BLOCK", enabled: true },
    { id: "POL-003", name: "License Compliance Gate", action: "BLOCK", enabled: true },
    { id: "POL-004", name: "Dependency Age Check", action: "WARN", enabled: true },
    { id: "POL-005", name: "Container Image Scanning", action: "AUDIT", enabled: true },
    { id: "POL-006", name: "CVSS Score Threshold (>=9.0)", action: "BLOCK", enabled: true },
  ];

  const actionColors: Record<string, string> = {
    BLOCK: "bg-red-500/20 text-red-400",
    WARN: "bg-yellow-500/20 text-yellow-400",
    AUDIT: "bg-blue-500/20 text-blue-400",
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">{t("title")}</h1>
      <p className="text-[var(--text-secondary)] mb-6">{t("subtitle")}</p>

      {/* Security Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {securityStats.map((stat) => (
          <div key={stat.label} className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)]">
            <div className="text-2xl mb-1">{stat.icon}</div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm text-[var(--text-secondary)]">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Codex Security Engine */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)] mb-6">
        <h2 className="text-lg font-semibold mb-1">Codex Security Engine</h2>
        <p className="text-sm text-[var(--text-secondary)] mb-4">
          Enterprise-grade code security: SAST, SCA, secret detection, license compliance, IaC scanning, SBOM
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {codexCapabilities.map((cap) => (
            <div key={cap.name} className="bg-[var(--bg-primary)] rounded-lg p-4 border border-[var(--border)]">
              <div className={`font-bold ${cap.color}`}>{cap.name}</div>
              <div className="text-xs text-[var(--text-secondary)] mb-2">{cap.fullName}</div>
              <div className="text-xs space-y-1">
                {cap.rules > 0 && <div>Rules: <span className="font-mono">{cap.rules}</span></div>}
                {cap.cwes > 0 && <div>CWE Coverage: <span className="font-mono">{cap.cwes}</span></div>}
                <div className="text-[var(--text-secondary)]">{cap.languages}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Frameworks */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)] mb-6">
        <h2 className="text-lg font-semibold mb-4">Compliance Frameworks</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {complianceFrameworks.map((fw) => (
            <div key={fw.name} className="bg-[var(--bg-primary)] rounded-lg p-4 border border-[var(--border)]">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold">{fw.name}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs ${statusColors[fw.status]}`}>
                  {fw.status}
                </span>
              </div>
              <div className="text-xs text-[var(--text-secondary)] mb-2">
                {fw.controls} controls
              </div>
              {fw.status === "active" && (
                <div className="w-full bg-[var(--border)] rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${fw.passRate >= 80 ? "bg-green-500" : fw.passRate >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                    style={{ width: `${fw.passRate}%` }}
                  />
                </div>
              )}
              {fw.status === "active" && (
                <div className="text-xs text-right mt-1 text-[var(--text-secondary)]">{fw.passRate}% pass</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Security Policies */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)] mb-6">
        <h2 className="text-lg font-semibold mb-4">Security Policies</h2>
        <div className="space-y-2">
          {policyRules.map((pol) => (
            <div key={pol.id} className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0">
              <div className="flex items-center gap-3">
                <code className="text-xs font-mono text-[var(--accent)]">{pol.id}</code>
                <span className="text-sm">{pol.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-0.5 rounded-full text-xs ${actionColors[pol.action]}`}>
                  {pol.action}
                </span>
                <span className={`w-2 h-2 rounded-full ${pol.enabled ? "bg-green-500" : "bg-gray-500"}`} />
              </div>
            </div>
          ))}
        </div>
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

      {/* Dangerous Commands */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)]">
        <h2 className="text-lg font-semibold mb-4">{t("dangerousCommands")}</h2>
        <div className="space-y-2">
          {dangerousCommands.map((cmd) => (
            <div key={cmd.pattern} className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0">
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
