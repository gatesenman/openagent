"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import type { Session } from "@/lib/api";

const statusColors: Record<string, string> = {
  created: "bg-zinc-400",
  running: "bg-[var(--success)]",
  paused: "bg-[var(--warning)]",
  completed: "bg-sky-400",
  failed: "bg-[var(--error)]",
};

export function SessionList() {
  const t = useTranslations("session");
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    setSessions([
      {
        id: "demo-1",
        title: "Implement user auth module",
        status: "running",
        mode: "cloud",
        model: "gpt-4o",
        platform: "linux",
        language: "en",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: "demo-2",
        title: "Fix API performance issue",
        status: "completed",
        mode: "localhost",
        model: "deepseek-chat",
        platform: "linux",
        language: "en",
        created_at: new Date(Date.now() - 3600000).toISOString(),
        updated_at: new Date(Date.now() - 1800000).toISOString(),
      },
      {
        id: "demo-3",
        title: "Add unit tests",
        status: "created",
        mode: "cascade",
        model: "qwen-plus",
        platform: "linux",
        language: "en",
        created_at: new Date(Date.now() - 7200000).toISOString(),
        updated_at: new Date(Date.now() - 7200000).toISOString(),
      },
    ]);
  }, []);

  return (
    <div className="flex-1 overflow-y-auto">
      {sessions.map((session) => (
        <button
          key={session.id}
          onClick={() => setSelected(session.id)}
          className={cn(
            "w-full px-3 py-2.5 text-left border-b border-[var(--border-subtle)] transition-all duration-100",
            selected === session.id
              ? "bg-[var(--accent-dim)]"
              : "hover:bg-white/[0.02]"
          )}
        >
          <div className="flex items-center gap-1.5 mb-0.5">
            <span className={cn("w-[5px] h-[5px] rounded-full flex-shrink-0", statusColors[session.status] || "bg-zinc-500")} />
            <span className="text-[12px] font-medium truncate text-[var(--text-primary)]">
              {session.title}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-[var(--text-secondary)] pl-[11px]">
            <span>{session.mode}</span>
            <span className="opacity-30">|</span>
            <span className="font-mono">{session.model}</span>
          </div>
        </button>
      ))}

      {sessions.length === 0 && (
        <div className="p-4 text-center text-[var(--text-secondary)] text-[11px]">
          {t("noSessions")}
        </div>
      )}
    </div>
  );
}
