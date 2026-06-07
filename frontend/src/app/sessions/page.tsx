"use client";

import { useTranslations } from "next-intl";
import { SessionList } from "@/components/session/SessionList";

export default function SessionsPage() {
  const t = useTranslations("session");

  return (
    <div className="flex h-full">
      {/* Session list */}
      <div className="w-[260px] border-r border-[var(--border)] flex flex-col bg-[var(--bg-secondary)]">
        <div className="panel-header">
          <span className="text-[11px] font-medium uppercase tracking-wider">{t("title")}</span>
        </div>
        <SessionList />
      </div>

      {/* Empty state */}
      <div className="flex-1 flex flex-col items-center justify-center">
        <svg className="w-10 h-10 text-[var(--text-secondary)]/20 mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        <p className="text-xs text-[var(--text-secondary)]">{t("noSessions")}</p>
      </div>
    </div>
  );
}
