"use client";

import { useTranslations } from "next-intl";
import { IconTerminal, IconZap, IconGlobe } from "@/components/icons/Icons";
import { ReactNode } from "react";

export default function HomePage() {
  const t = useTranslations("session");

  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          OpenAgent
        </h1>
        <p className="text-[var(--text-secondary)] text-lg">
          AI-Driven Full Lifecycle Software Development Platform
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl w-full mb-8">
        <FeatureCard
          title="Localhost Mode"
          description="Local LLM via Ollama, data stays on-premises"
          icon={<IconTerminal className="w-7 h-7 text-indigo-400" />}
        />
        <FeatureCard
          title="Cascade Mode"
          description="Editor integration, real-time collaborative dev"
          icon={<IconZap className="w-7 h-7 text-yellow-400" />}
        />
        <FeatureCard
          title="Cloud Mode"
          description="Remote virtual environment, full-featured Agent"
          icon={<IconGlobe className="w-7 h-7 text-blue-400" />}
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
  icon: ReactNode;
}) {
  return (
    <div className="p-4 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--accent)] transition-colors">
      <div className="mb-2">{icon}</div>
      <h3 className="font-semibold mb-1">{title}</h3>
      <p className="text-sm text-[var(--text-secondary)]">{description}</p>
    </div>
  );
}
