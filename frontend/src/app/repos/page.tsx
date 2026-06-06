"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface Repo {
  id: string;
  name: string;
  language: string;
  description: string;
  deepwiki_status: string;
  codemap_status: string;
}

export default function ReposPage() {
  const t = useTranslations("repos");
  const [repos] = useState<Repo[]>([
    { id: "1", name: "openagent/backend", language: "Python", description: "FastAPI 后端服务", deepwiki_status: "ready", codemap_status: "ready" },
    { id: "2", name: "openagent/frontend", language: "TypeScript", description: "Next.js 前端应用", deepwiki_status: "ready", codemap_status: "indexing" },
    { id: "3", name: "openagent/docs", language: "Markdown", description: "项目文档", deepwiki_status: "pending", codemap_status: "pending" },
  ]);

  const statusIcon = (status: string) => {
    switch (status) {
      case "ready": return <span className="text-green-400">●</span>;
      case "indexing": return <span className="text-yellow-400 animate-pulse">●</span>;
      default: return <span className="text-zinc-500">○</span>;
    }
  };

  const langColors: Record<string, string> = {
    Python: "bg-blue-500/20 text-blue-400",
    TypeScript: "bg-cyan-500/20 text-cyan-400",
    Markdown: "bg-purple-500/20 text-purple-400",
    Rust: "bg-orange-500/20 text-orange-400",
    Go: "bg-teal-500/20 text-teal-400",
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm">
          {t("addRepo")}
        </button>
      </div>

      <div className="space-y-3">
        {repos.map((repo) => (
          <div
            key={repo.id}
            className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] hover:border-[var(--accent)]/50 transition"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-xl">📁</span>
                <div>
                  <div className="font-medium">{repo.name}</div>
                  <div className="text-sm text-[var(--text-secondary)]">{repo.description}</div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className={`px-2 py-0.5 rounded-full text-xs ${langColors[repo.language] || "bg-zinc-700 text-zinc-300"}`}>
                  {repo.language}
                </span>
                <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)]">
                  <span className="flex items-center gap-1">
                    {statusIcon(repo.deepwiki_status)} DeepWiki
                  </span>
                  <span className="flex items-center gap-1">
                    {statusIcon(repo.codemap_status)} CodeMap
                  </span>
                </div>
                <button className="text-xs text-[var(--accent)] hover:underline">
                  {t("index")}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
