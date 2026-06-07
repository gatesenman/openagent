"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { IconTerminal, IconZap, IconGlobe } from "@/components/icons/Icons";
import { ReactNode } from "react";

export default function HomePage() {
  const t = useTranslations("session");
  const router = useRouter();
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      router.push(`/sessions/new?prompt=${encodeURIComponent(input)}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full px-8">
      <div className="max-w-xl w-full">
        {/* App title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[var(--accent)] mb-4">
            <span className="text-lg font-bold text-white">OA</span>
          </div>
          <h1 className="text-2xl font-semibold mb-1 text-[var(--text-primary)]">
            OpenAgent
          </h1>
          <p className="text-xs text-[var(--text-secondary)] tracking-wide uppercase">
            Cross-Platform Code Agent Desktop
          </p>
        </div>

        {/* Command input */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="relative bg-[var(--surface)] border border-[var(--border)] rounded-lg overflow-hidden focus-within:border-[var(--accent)]/40 transition-colors">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("placeholder")}
              rows={2}
              className="w-full bg-transparent px-4 py-3 text-sm resize-none focus:outline-none text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <div className="flex items-center justify-between px-3 pb-2">
              <span className="text-[10px] text-[var(--text-secondary)]">Shift+Enter for new line</span>
              <button
                type="submit"
                disabled={!input.trim()}
                className="px-3 py-1 bg-[var(--accent)] hover:bg-[var(--accent-hover)] disabled:opacity-30 text-white text-xs font-medium rounded transition-colors"
              >
                Start Session
              </button>
            </div>
          </div>
        </form>

        {/* Mode selector */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          <ModeCard
            title="Localhost"
            desc="Ollama local LLM"
            icon={<IconTerminal className="w-4 h-4 text-emerald-400" />}
            active
          />
          <ModeCard
            title="Cascade"
            desc="Editor integration"
            icon={<IconZap className="w-4 h-4 text-amber-400" />}
          />
          <ModeCard
            title="Cloud"
            desc="Remote sandbox"
            icon={<IconGlobe className="w-4 h-4 text-sky-400" />}
          />
        </div>

        {/* Recent */}
        <div>
          <div className="panel-header rounded-t-md">Recent Sessions</div>
          <div className="bg-[var(--surface)] border border-t-0 border-[var(--border)] rounded-b-md p-4">
            <p className="text-xs text-[var(--text-secondary)] text-center">{t("noSessions")}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ModeCard({ title, desc, icon, active }: { title: string; desc: string; icon: ReactNode; active?: boolean }) {
  return (
    <div className={cn(
      "p-3 rounded-md border cursor-pointer transition-all duration-150",
      active
        ? "border-[var(--accent)]/40 bg-[var(--accent-dim)]"
        : "border-[var(--border)] bg-[var(--surface)] hover:border-[var(--border)]/80"
    )}>
      <div className="mb-1.5">{icon}</div>
      <div className="text-xs font-medium text-[var(--text-primary)]">{title}</div>
      <div className="text-[10px] text-[var(--text-secondary)]">{desc}</div>
    </div>
  );
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}
