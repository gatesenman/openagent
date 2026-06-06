"use client";

import { useTranslations } from "next-intl";

export default function HomePage() {
  const t = useTranslations("session");

  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          OpenAgent
        </h1>
        <p className="text-[var(--text-secondary)] text-lg">
          AI 驱动的全生命周期软件开发平台
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl w-full mb-8">
        <FeatureCard
          title="本地模式"
          description="使用本地 LLM（Ollama），数据不出域"
          icon="💻"
        />
        <FeatureCard
          title="Cascade 模式"
          description="编辑器集成，实时协作开发"
          icon="⚡"
        />
        <FeatureCard
          title="云端模式"
          description="远程虚拟环境，全功能 Agent"
          icon="☁️"
        />
      </div>

      <p className="text-[var(--text-secondary)]">{t("noSessions")}</p>
    </div>
  );
}

function FeatureCard({
  title,
  description,
  icon,
}: {
  title: string;
  description: string;
  icon: string;
}) {
  return (
    <div className="p-4 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--accent)] transition-colors">
      <div className="text-2xl mb-2">{icon}</div>
      <h3 className="font-semibold mb-1">{title}</h3>
      <p className="text-sm text-[var(--text-secondary)]">{description}</p>
    </div>
  );
}
