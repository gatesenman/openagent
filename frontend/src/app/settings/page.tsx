"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

type SettingsTab =
  | "general" | "connections" | "sessions" | "plans"
  | "agent" | "review" | "deepwiki" | "schedules"
  | "desktop" | "skills" | "environment" | "knowledge"
  | "playbooks" | "secrets" | "repos" | "membership"
  | "apikeys" | "security" | "analytics";

const settingsGroups = [
  {
    label: "Personal",
    items: [
      { key: "general" as const, label: "General" },
      { key: "connections" as const, label: "Connections" },
    ],
  },
  {
    label: "Organization",
    items: [
      { key: "sessions" as const, label: "Sessions" },
      { key: "plans" as const, label: "Plans & Billing" },
      { key: "membership" as const, label: "Membership" },
      { key: "apikeys" as const, label: "API Keys" },
    ],
  },
  {
    label: "Agent",
    items: [
      { key: "agent" as const, label: "Agent Config" },
      { key: "review" as const, label: "Review" },
      { key: "deepwiki" as const, label: "DeepWiki" },
      { key: "schedules" as const, label: "Schedules" },
      { key: "desktop" as const, label: "Desktop" },
    ],
  },
  {
    label: "Configuration",
    items: [
      { key: "skills" as const, label: "Skills & Rules" },
      { key: "environment" as const, label: "Environment" },
      { key: "knowledge" as const, label: "Knowledge" },
      { key: "playbooks" as const, label: "Playbooks" },
      { key: "secrets" as const, label: "Secrets" },
      { key: "repos" as const, label: "Repositories" },
      { key: "security" as const, label: "Security" },
      { key: "analytics" as const, label: "Analytics" },
    ],
  },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");

  return (
    <div className="flex h-full">
      {/* Left menu */}
      <div className="w-[200px] border-r border-[var(--border)] overflow-y-auto bg-[var(--bg-secondary)]">
        <div className="panel-header">
          <span className="text-[11px] font-medium uppercase tracking-wider">Settings</span>
        </div>
        <div className="p-2">
        {settingsGroups.map((group) => (
          <div key={group.label} className="mb-3">
            <h3 className="text-[10px] text-[var(--text-secondary)] mb-1 px-2 uppercase tracking-wider font-medium">{group.label}</h3>
            <nav className="space-y-px">
              {group.items.map((item) => (
                <button
                  key={item.key}
                  onClick={() => setActiveTab(item.key)}
                  className={cn(
                    "w-full text-left px-2 py-1 rounded text-[12px] transition-all duration-100",
                    activeTab === item.key
                      ? "bg-[var(--accent-dim)] text-[var(--accent)]"
                      : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/[0.02]"
                  )}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        ))}
        </div>
      </div>

      {/* Right content */}
      <div className="flex-1 overflow-y-auto p-5">
        <div className="max-w-2xl mx-auto space-y-4">
          {activeTab === "general" && <GeneralSettings />}
          {activeTab === "connections" && <ConnectionsSettings />}
          {activeTab === "sessions" && <SessionsSettings />}
          {activeTab === "plans" && <PlansSettings />}
          {activeTab === "membership" && <MembershipSettings />}
          {activeTab === "apikeys" && <ApiKeysSettings />}
          {activeTab === "agent" && <AgentSettings />}
          {activeTab === "review" && <ReviewSettings />}
          {activeTab === "deepwiki" && <DeepWikiSettings />}
          {activeTab === "schedules" && <SchedulesSettings />}
          {activeTab === "desktop" && <DesktopSettings />}
          {activeTab === "skills" && <SkillsSettings />}
          {activeTab === "environment" && <EnvironmentSettings />}
          {activeTab === "knowledge" && <KnowledgeSettings />}
          {activeTab === "playbooks" && <PlaybooksSettings />}
          {activeTab === "secrets" && <SecretsSettings />}
          {activeTab === "repos" && <ReposSettings />}
          {activeTab === "security" && <SecuritySettings />}
          {activeTab === "analytics" && <AnalyticsSettings />}
        </div>
      </div>
    </div>
  );
}

function SettingItem({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-[var(--border-subtle)]">
      <div>
        <p className="text-[12px] font-medium text-[var(--text-primary)]">{label}</p>
        {description && <p className="text-[10px] text-[var(--text-secondary)] mt-0.5">{description}</p>}
      </div>
      <div>{children}</div>
    </div>
  );
}

function SelectInput({ options, defaultValue }: { options: { value: string; label: string }[]; defaultValue?: string }) {
  return (
    <select defaultValue={defaultValue} className="bg-[var(--surface)] border border-[var(--border)] rounded-md px-2 py-1 text-[11px] text-[var(--text-secondary)]">
      {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );
}

function GeneralSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">General</h3>
      <SettingItem label="Language" description="Interface language">
        <SelectInput options={[{ value: "zh", label: "Chinese" }, { value: "en", label: "English" }]} />
      </SettingItem>
      <SettingItem label="Theme" description="Dark / Light theme">
        <SelectInput options={[{ value: "dark", label: "Dark" }, { value: "light", label: "Light" }]} />
      </SettingItem>
      <SettingItem label="Default Mode" description="Agent execution mode">
        <SelectInput options={[{ value: "cloud", label: "Cloud" }, { value: "localhost", label: "Localhost" }, { value: "cascade", label: "Cascade" }]} />
      </SettingItem>
    </div>
  );
}

function ConnectionsSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Connections</h3>
      <SettingItem label="GitHub" description="Connect GitHub account">
        <button className="px-3 py-1 text-sm border border-[var(--border)] rounded hover:bg-white/5">Connect</button>
      </SettingItem>
      <SettingItem label="GitLab" description="Connect GitLab account">
        <button className="px-3 py-1 text-sm border border-[var(--border)] rounded hover:bg-white/5">Connect</button>
      </SettingItem>
      <SettingItem label="Slack" description="Notifications integration">
        <button className="px-3 py-1 text-sm border border-[var(--border)] rounded hover:bg-white/5">Connect</button>
      </SettingItem>
    </div>
  );
}

function SessionsSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Sessions</h3>
      <SettingItem label="Auto-continue" description="Allow Agent to continue without confirmation">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
      <SettingItem label="Max iterations" description="Maximum ReAct loop steps">
        <input type="number" min="1" max="200" defaultValue="50" className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-20" />
      </SettingItem>
      <SettingItem label="Auto-fix lints" description="Automatically fix lint errors">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
    </div>
  );
}

function PlansSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Plans & Billing</h3>
      <div className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium">Current Plan</span>
          <span className="px-2 py-0.5 rounded text-xs bg-indigo-500/20 text-indigo-400">Team</span>
        </div>
        <div className="text-2xl font-bold">$499<span className="text-sm text-[var(--text-secondary)]">/mo</span></div>
        <div className="text-xs text-[var(--text-secondary)] mt-1">Renews: 2026-07-01</div>
      </div>
      <SettingItem label="ACU Used" description="Agent Compute Units this cycle">
        <span className="text-sm font-mono">1,284 / 5,000</span>
      </SettingItem>
    </div>
  );
}

function MembershipSettings() {
  const members = [
    { name: "Admin User", email: "admin@company.com", role: "admin" },
    { name: "Developer", email: "dev@company.com", role: "member" },
  ];
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Membership</h3>
        <button className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg">Invite Member</button>
      </div>
      <div className="space-y-2">
        {members.map((m) => (
          <div key={m.email} className="flex items-center justify-between py-2 border-b border-[var(--border)]">
            <div>
              <div className="text-sm font-medium">{m.name}</div>
              <div className="text-xs text-[var(--text-secondary)]">{m.email}</div>
            </div>
            <span className="text-xs px-2 py-0.5 rounded bg-[var(--bg-secondary)]">{m.role}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ApiKeysSettings() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">API Keys</h3>
        <button className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg">Create Service User</button>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">Manage service users and API access credentials</p>
    </div>
  );
}

function AgentSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Agent Configuration</h3>
      <SettingItem label="Default Model" description="LLM for Agent execution">
        <SelectInput options={[
          { value: "gpt-4o", label: "GPT-4o" },
          { value: "deepseek-chat", label: "DeepSeek Chat" },
          { value: "claude-sonnet-4", label: "Claude Sonnet 4" },
          { value: "qwen-plus", label: "Qwen Plus" },
          { value: "llama3", label: "Llama 3 (Local)" },
        ]} />
      </SettingItem>
      <SettingItem label="Temperature" description="0.0-1.0, lower is more deterministic">
        <input type="number" min="0" max="1" step="0.1" defaultValue="0.1" className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-20" />
      </SettingItem>
      <SettingItem label="Sandbox Type" description="Container or local process">
        <SelectInput options={[{ value: "docker", label: "Docker Container" }, { value: "local", label: "Local Process" }]} />
      </SettingItem>
      <SettingItem label="Docker Image" description="Base image for sandbox">
        <input type="text" defaultValue="ubuntu:22.04" className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-40" />
      </SettingItem>
    </div>
  );
}

function ReviewSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Review</h3>
      <SettingItem label="Auto-review PRs" description="Agent reviews PRs automatically">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
      <SettingItem label="Review depth" description="Security / Code quality / Performance">
        <SelectInput options={[{ value: "standard", label: "Standard" }, { value: "deep", label: "Deep" }, { value: "security", label: "Security-focused" }]} />
      </SettingItem>
    </div>
  );
}

function DeepWikiSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">DeepWiki</h3>
      <SettingItem label="Auto-index" description="Automatically index repos on connect">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
      <SettingItem label="Embedding model" description="Model for symbol embeddings">
        <SelectInput options={[{ value: "openai", label: "OpenAI ada-002" }, { value: "local", label: "Local (all-MiniLM-L6)" }]} />
      </SettingItem>
    </div>
  );
}

function SchedulesSettings() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Schedules</h3>
        <button className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg">Create Schedule</button>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">Configure scheduled tasks for Agent to run periodically</p>
    </div>
  );
}

function DesktopSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Desktop</h3>
      <SettingItem label="Resolution" description="Virtual desktop resolution">
        <SelectInput options={[{ value: "1280x800", label: "1280 x 800" }, { value: "1920x1080", label: "1920 x 1080" }]} />
      </SettingItem>
      <SettingItem label="Auto-screenshot" description="Capture screenshots during agent work">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
    </div>
  );
}

function SkillsSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Skills & Rules</h3>
      <SettingItem label="Global rules" description="Rules applied to all sessions">
        <button className="px-3 py-1 text-sm border border-[var(--border)] rounded hover:bg-white/5">Edit</button>
      </SettingItem>
      <SettingItem label="AGENTS.md" description="Auto-discover repo agent configs">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
    </div>
  );
}

function EnvironmentSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Environment</h3>
      <SettingItem label="Blueprint" description="Devbox initialization YAML">
        <button className="px-3 py-1 text-sm border border-[var(--border)] rounded hover:bg-white/5">Edit Blueprint</button>
      </SettingItem>
      <SettingItem label="Snapshots" description="Environment snapshot management">
        <button className="px-3 py-1 text-sm border border-[var(--border)] rounded hover:bg-white/5">Manage</button>
      </SettingItem>
    </div>
  );
}

function KnowledgeSettings() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Knowledge</h3>
        <button className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg">Add Note</button>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">Three-layer knowledge system: System / User / Repo</p>
    </div>
  );
}

function PlaybooksSettings() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Playbooks</h3>
        <button className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg">Create Playbook</button>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">Reusable task templates for Agent automation</p>
    </div>
  );
}

function SecretsSettings() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Secrets</h3>
        <button className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg">Add Secret</button>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">Manage API Keys, passwords, and credentials (org/user/repo scope)</p>
    </div>
  );
}

function ReposSettings() {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Repositories</h3>
        <button className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg">Add Repository</button>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">Manage connected Git repos, trigger DeepWiki indexing and CodeMap analysis</p>
    </div>
  );
}

function SecuritySettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Security</h3>
      <SettingItem label="Codex Security" description="Enterprise-grade code scanning">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
      <SettingItem label="OWASP LLM Top 10" description="AI-specific security rules">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
      <SettingItem label="Command allowlist" description="Restrict executable commands">
        <button className="px-3 py-1 text-sm border border-[var(--border)] rounded hover:bg-white/5">Configure</button>
      </SettingItem>
      <SettingItem label="Authentication" description="JWT / OAuth / OIDC">
        <SelectInput options={[{ value: "jwt", label: "JWT" }, { value: "oauth", label: "OAuth 2.0" }, { value: "oidc", label: "OIDC" }]} />
      </SettingItem>
    </div>
  );
}

function AnalyticsSettings() {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-3">Analytics</h3>
      <div className="grid grid-cols-2 gap-4">
        {[
          { label: "LLM Calls", value: "1,284" },
          { label: "Tool Calls", value: "3,456" },
          { label: "Sessions", value: "89" },
          { label: "Sandbox Usage", value: "42" },
        ].map((s) => (
          <div key={s.label} className="bg-[var(--bg-secondary)] rounded-lg p-3 border border-[var(--border)]">
            <div className="text-xs text-[var(--text-secondary)]">{s.label}</div>
            <div className="text-xl font-bold mt-1">{s.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
