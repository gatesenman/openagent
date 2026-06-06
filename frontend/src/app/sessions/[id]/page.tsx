"use client";

import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { SessionDetail } from "@/components/session/SessionDetail";

export default function SessionPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const t = useTranslations("session");

  return (
    <div className="flex h-full">
      {/* 左侧信息面板 */}
      <div className="w-72 border-r border-[var(--border)] bg-[var(--bg-secondary)] flex flex-col">
        <div className="p-4 border-b border-[var(--border)]">
          <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
            {t("info")}
          </h3>
        </div>
        <div className="p-4 space-y-4 text-sm">
          <div>
            <span className="text-[var(--text-secondary)]">ID: </span>
            <span className="font-mono text-xs">{sessionId.slice(0, 8)}...</span>
          </div>
          <div>
            <span className="text-[var(--text-secondary)]">{t("status")}: </span>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-green-500/20 text-green-400">
              ● {t("running")}
            </span>
          </div>
          <div>
            <span className="text-[var(--text-secondary)]">{t("mode")}: </span>
            <span>Docker Sandbox</span>
          </div>
          <div>
            <span className="text-[var(--text-secondary)]">{t("model")}: </span>
            <span>GPT-4o</span>
          </div>
          <div>
            <span className="text-[var(--text-secondary)]">{t("platform")}: </span>
            <span>Ubuntu 22.04</span>
          </div>
        </div>

        {/* Agent 工具列表 */}
        <div className="p-4 border-t border-[var(--border)]">
          <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase mb-2">
            {t("tools")}
          </h4>
          <div className="space-y-1">
            {["shell_exec", "file_read", "file_write", "search_code", "git_ops"].map(
              (tool) => (
                <div
                  key={tool}
                  className="text-xs font-mono py-1 px-2 rounded bg-[var(--bg-primary)] text-[var(--text-secondary)]"
                >
                  {tool}
                </div>
              )
            )}
          </div>
        </div>
      </div>

      {/* 右侧 5-Panel 交互区 */}
      <div className="flex-1">
        <SessionDetail sessionId={sessionId} />
      </div>
    </div>
  );
}
