"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

type SettingsTab = "general" | "models" | "sandbox" | "security";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");

  return (
    <div className="flex h-full">
      {/* 左侧菜单 */}
      <div className="w-56 border-r border-[var(--border)] p-4">
        <h2 className="text-lg font-semibold mb-4">{t("title")}</h2>
        <nav className="space-y-1">
          {(["general", "models", "sandbox", "security"] as const).map(
            (tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
                  activeTab === tab
                    ? "bg-[var(--accent)]/10 text-[var(--accent)]"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                )}
              >
                {t(tab)}
              </button>
            )
          )}
        </nav>
      </div>

      {/* 右侧内容 */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {activeTab === "general" && <GeneralSettings />}
          {activeTab === "models" && <ModelSettings />}
          {activeTab === "sandbox" && <SandboxSettings />}
          {activeTab === "security" && <SecuritySettings />}
        </div>
      </div>
    </div>
  );
}

function SettingItem({
  label,
  description,
  children,
}: {
  label: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-[var(--border)]">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {description && (
          <p className="text-xs text-[var(--text-secondary)]">{description}</p>
        )}
      </div>
      <div>{children}</div>
    </div>
  );
}

function GeneralSettings() {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">通用设置</h3>
      <SettingItem label="界面语言" description="选择默认界面语言">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
      </SettingItem>
      <SettingItem label="主题" description="暗色 / 亮色主题切换">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="dark">暗色</option>
          <option value="light">亮色</option>
        </select>
      </SettingItem>
      <SettingItem label="默认运行模式">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="cloud">云端模式</option>
          <option value="localhost">本地模式</option>
          <option value="cascade">Cascade 模式</option>
        </select>
      </SettingItem>
    </div>
  );
}

function ModelSettings() {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">模型设置</h3>
      <SettingItem label="默认模型" description="Agent 使用的默认 LLM">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="gpt-4o">GPT-4o</option>
          <option value="deepseek-chat">DeepSeek Chat</option>
          <option value="deepseek-coder">DeepSeek Coder</option>
          <option value="qwen-plus">Qwen Plus</option>
          <option value="claude-sonnet-4">Claude Sonnet 4</option>
          <option value="llama3">Llama 3 (本地)</option>
        </select>
      </SettingItem>
      <SettingItem label="采样温度" description="0.0-1.0，越低越确定">
        <input
          type="number"
          min="0"
          max="1"
          step="0.1"
          defaultValue="0.1"
          className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-20"
        />
      </SettingItem>
      <SettingItem label="最大迭代次数" description="ReAct 循环最大轮数">
        <input
          type="number"
          min="1"
          max="200"
          defaultValue="50"
          className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-20"
        />
      </SettingItem>
      <SettingItem label="API Key" description="配置 LLM API Key">
        <input
          type="password"
          placeholder="sk-..."
          className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-48"
        />
      </SettingItem>
    </div>
  );
}

function SandboxSettings() {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">沙箱设置</h3>
      <SettingItem label="沙箱类型" description="Docker 容器或本地进程">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="docker">Docker 容器</option>
          <option value="local">本地进程</option>
        </select>
      </SettingItem>
      <SettingItem label="CPU 限制" description="每个沙箱的 CPU 限制">
        <input
          type="number"
          min="0.5"
          max="8"
          step="0.5"
          defaultValue="2"
          className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-20"
        />
      </SettingItem>
      <SettingItem label="内存限制" description="每个沙箱的内存限制">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="512m">512 MB</option>
          <option value="1g">1 GB</option>
          <option value="2g" selected>2 GB</option>
          <option value="4g">4 GB</option>
        </select>
      </SettingItem>
      <SettingItem label="Docker 镜像" description="沙箱使用的基础镜像">
        <input
          type="text"
          defaultValue="ubuntu:22.04"
          className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm w-48"
        />
      </SettingItem>
    </div>
  );
}

function SecuritySettings() {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">安全设置</h3>
      <SettingItem label="安全模式" description="危险操作需要确认">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
      <SettingItem label="命令白名单" description="限制可执行的命令">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="ask">需要确认</option>
          <option value="auto">自动执行</option>
          <option value="deny">禁止执行</option>
        </select>
      </SettingItem>
      <SettingItem label="敏感数据检测" description="检测输出中的密码/密钥">
        <input type="checkbox" defaultChecked className="w-4 h-4 accent-[var(--accent)]" />
      </SettingItem>
      <SettingItem label="网络访问" description="沙箱的网络访问权限">
        <select className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm">
          <option value="full">完全访问</option>
          <option value="limited">受限访问</option>
          <option value="none">禁止访问</option>
        </select>
      </SettingItem>
    </div>
  );
}
