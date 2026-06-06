"use client";

import { useTranslations } from "next-intl";
import { SessionList } from "@/components/session/SessionList";

export default function SessionsPage() {
  const t = useTranslations("session");

  return (
    <div className="flex h-full">
      {/* 左侧会话列表 */}
      <div className="w-80 border-r border-[var(--border)] flex flex-col">
        <div className="p-4 border-b border-[var(--border)]">
          <h2 className="text-lg font-semibold">{t("title")}</h2>
        </div>
        <SessionList />
      </div>

      {/* 右侧选择提示 */}
      <div className="flex-1 flex items-center justify-center text-[var(--text-secondary)]">
        {t("noSessions")}
      </div>
    </div>
  );
}
