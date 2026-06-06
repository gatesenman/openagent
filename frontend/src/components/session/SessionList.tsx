"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import type { Session } from "@/lib/api";

const statusColors: Record<string, string> = {
  created: "bg-gray-400",
  running: "bg-[var(--success)]",
  paused: "bg-[var(--warning)]",
  completed: "bg-blue-400",
  failed: "bg-[var(--error)]",
};

export function SessionList() {
  const t = useTranslations("session");
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    // mock 数据
    setSessions([
      {
        id: "demo-1",
        title: "实现用户登录模块",
        status: "running",
        mode: "cloud",
        model: "gpt-4o",
        platform: "linux",
        language: "zh",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: "demo-2",
        title: "修复API性能问题",
        status: "completed",
        mode: "localhost",
        model: "deepseek-chat",
        platform: "linux",
        language: "zh",
        created_at: new Date(Date.now() - 3600000).toISOString(),
        updated_at: new Date(Date.now() - 1800000).toISOString(),
      },
      {
        id: "demo-3",
        title: "添加单元测试",
        status: "created",
        mode: "cascade",
        model: "qwen-plus",
        platform: "linux",
        language: "zh",
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
            "w-full px-4 py-3 text-left border-b border-[var(--border)] transition-colors",
            selected === session.id
              ? "bg-[var(--accent)]/10"
              : "hover:bg-white/5"
          )}
        >
          <div className="flex items-center gap-2 mb-1">
            <span
              className={cn(
                "w-2 h-2 rounded-full",
                statusColors[session.status] || "bg-gray-400"
              )}
            />
            <span className="font-medium text-sm truncate">
              {session.title}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
            <span>{t(`mode.${session.mode}`)}</span>
            <span>·</span>
            <span>{session.model}</span>
            <span>·</span>
            <span>{t(`status.${session.status}`)}</span>
          </div>
        </button>
      ))}

      {sessions.length === 0 && (
        <div className="p-4 text-center text-[var(--text-secondary)] text-sm">
          {t("noSessions")}
        </div>
      )}
    </div>
  );
}
