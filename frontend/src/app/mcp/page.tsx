"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface MCPServer {
  id: string;
  name: string;
  description: string;
  category: string;
  status: string;
  tools_count: number;
}

export default function MCPMarketPage() {
  const t = useTranslations("mcp");
  const [servers] = useState<MCPServer[]>([
    { id: "1", name: "GitHub", description: "仓库管理、PR、Issues、Actions", category: "开发工具", status: "installed", tools_count: 12 },
    { id: "2", name: "Slack", description: "消息发送、频道管理", category: "沟通协作", status: "installed", tools_count: 5 },
    { id: "3", name: "PostgreSQL", description: "数据库查询、Schema 管理", category: "数据库", status: "available", tools_count: 8 },
    { id: "4", name: "Sentry", description: "错误监控、性能追踪", category: "监控", status: "available", tools_count: 6 },
    { id: "5", name: "Jira", description: "项目管理、任务跟踪", category: "项目管理", status: "available", tools_count: 10 },
    { id: "6", name: "Docker", description: "容器管理、镜像构建", category: "基础设施", status: "installed", tools_count: 7 },
    { id: "7", name: "Figma", description: "设计稿读取、UI 资产", category: "设计", status: "available", tools_count: 4 },
    { id: "8", name: "Notion", description: "知识库、文档管理", category: "知识管理", status: "available", tools_count: 6 },
  ]);
  const [filter, setFilter] = useState<string>("all");

  const categories = ["all", ...new Set(servers.map((s) => s.category))];
  const filtered = filter === "all" ? servers : servers.filter((s) => s.category === filter);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
      </div>

      <div className="flex gap-2 mb-6 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-3 py-1.5 rounded-full text-sm transition ${
              filter === cat
                ? "bg-[var(--accent)] text-white"
                : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:text-white"
            }`}
          >
            {cat === "all" ? t("all") : cat}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {filtered.map((server) => (
          <div
            key={server.id}
            className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] hover:border-[var(--accent)]/50 transition"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="font-medium text-lg">{server.name}</div>
                <div className="text-sm text-[var(--text-secondary)] mt-1">{server.description}</div>
                <div className="flex items-center gap-3 mt-3">
                  <span className="text-xs bg-zinc-700 text-zinc-300 px-2 py-0.5 rounded-full">
                    {server.category}
                  </span>
                  <span className="text-xs text-[var(--text-secondary)]">
                    {server.tools_count} {t("tools")}
                  </span>
                </div>
              </div>
              <button
                className={`px-3 py-1.5 rounded text-sm ${
                  server.status === "installed"
                    ? "bg-green-500/20 text-green-400"
                    : "bg-[var(--accent)] text-white hover:opacity-90"
                }`}
              >
                {server.status === "installed" ? t("installed") : t("install")}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
