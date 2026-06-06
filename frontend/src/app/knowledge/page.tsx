"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

type KnowledgeLayer = "system" | "user" | "repo";

interface KnowledgeEntry {
  id: string;
  name: string;
  content: string;
  scope: KnowledgeLayer;
  repo_path?: string;
  tags: string[];
  pinned: boolean;
  created_at: string;
}

const layerColors: Record<KnowledgeLayer, string> = {
  system: "bg-blue-500/20 text-blue-400",
  user: "bg-green-500/20 text-green-400",
  repo: "bg-purple-500/20 text-purple-400",
};

const layerLabels: Record<KnowledgeLayer, string> = {
  system: "System",
  user: "User",
  repo: "Repo",
};

const mockEntries: KnowledgeEntry[] = [
  {
    id: "1",
    name: "代码规范",
    content: "所有 Python 代码使用 ruff 格式化，TypeScript 使用 ESLint + Prettier。提交前必须通过 lint 检查。",
    scope: "user",
    tags: ["规范", "lint"],
    pinned: true,
    created_at: "2026-06-01T00:00:00Z",
  },
  {
    id: "2",
    name: "测试策略",
    content: "单元测试覆盖率 > 80%。API 测试使用 pytest + httpx TestClient。前端测试使用 vitest。",
    scope: "user",
    tags: ["测试"],
    pinned: false,
    created_at: "2026-06-02T00:00:00Z",
  },
  {
    id: "3",
    name: "AGENTS.md 解析",
    content: "自动从项目根目录 AGENTS.md 文件解析开发规范、技术栈、目录结构等信息，注入 Agent 上下文。",
    scope: "repo",
    repo_path: "openagent",
    tags: ["agent", "context"],
    pinned: false,
    created_at: "2026-06-03T00:00:00Z",
  },
  {
    id: "4",
    name: "危险命令拦截",
    content: "shell_exec 工具拦截以下命令模式: rm -rf /, DROP TABLE, mkfs, :(){ :|:& };:, chmod 777 /",
    scope: "system",
    tags: ["安全"],
    pinned: true,
    created_at: "2026-06-01T00:00:00Z",
  },
  {
    id: "5",
    name: "DeepWiki 文档格式",
    content: "5段式文档结构: Definition → Example Usages → Notes → See Also → Follow-up Questions。使用 AST 解析符号。",
    scope: "system",
    tags: ["deepwiki", "文档"],
    pinned: false,
    created_at: "2026-06-01T00:00:00Z",
  },
];

export default function KnowledgePage() {
  const t = useTranslations("nav");
  const [activeLayer, setActiveLayer] = useState<KnowledgeLayer | "all">("all");
  const [showCreate, setShowCreate] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);
  const [newName, setNewName] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newScope, setNewScope] = useState<KnowledgeLayer>("user");

  const filtered = activeLayer === "all"
    ? mockEntries
    : mockEntries.filter((e) => e.scope === activeLayer);

  return (
    <div className="flex h-full">
      {/* 左侧列表 */}
      <div className="w-80 border-r border-[var(--border)] flex flex-col">
        <div className="p-4 border-b border-[var(--border)]">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">{t("knowledge")}</h2>
            <button
              onClick={() => setShowCreate(!showCreate)}
              className="px-3 py-1 text-xs bg-[var(--accent)] text-white rounded hover:opacity-90"
            >
              + 新建
            </button>
          </div>

          {/* 三层筛选 */}
          <div className="flex gap-1">
            {(["all", "system", "user", "repo"] as const).map((layer) => (
              <button
                key={layer}
                onClick={() => setActiveLayer(layer)}
                className={cn(
                  "px-2 py-1 text-xs rounded transition-colors",
                  activeLayer === layer
                    ? "bg-[var(--accent)] text-white"
                    : "bg-[var(--bg-primary)] text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
                )}
              >
                {layer === "all" ? "全部" : layerLabels[layer]}
              </button>
            ))}
          </div>
        </div>

        {/* 创建表单 */}
        {showCreate && (
          <div className="p-4 border-b border-[var(--border)] bg-[var(--bg-secondary)] space-y-2">
            <input
              placeholder="知识名称"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full px-2 py-1 text-sm bg-[var(--bg-primary)] border border-[var(--border)] rounded"
            />
            <textarea
              placeholder="知识内容..."
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              rows={3}
              className="w-full px-2 py-1 text-sm bg-[var(--bg-primary)] border border-[var(--border)] rounded resize-none"
            />
            <div className="flex gap-2">
              <select
                value={newScope}
                onChange={(e) => setNewScope(e.target.value as KnowledgeLayer)}
                className="px-2 py-1 text-xs bg-[var(--bg-primary)] border border-[var(--border)] rounded"
              >
                <option value="user">User</option>
                <option value="repo">Repo</option>
              </select>
              <button className="px-3 py-1 text-xs bg-[var(--accent)] text-white rounded">
                保存
              </button>
            </div>
          </div>
        )}

        {/* 条目列表 */}
        <div className="flex-1 overflow-y-auto">
          {filtered.map((entry) => (
            <button
              key={entry.id}
              onClick={() => setSelectedEntry(entry)}
              className={cn(
                "w-full text-left px-4 py-3 border-b border-[var(--border)] hover:bg-[var(--bg-secondary)] transition-colors",
                selectedEntry?.id === entry.id && "bg-[var(--bg-secondary)]"
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                {entry.pinned && <span className="text-xs">📌</span>}
                <span className="text-sm font-medium truncate">{entry.name}</span>
                <span className={cn("px-1.5 py-0.5 text-[10px] rounded", layerColors[entry.scope])}>
                  {layerLabels[entry.scope]}
                </span>
              </div>
              <p className="text-xs text-[var(--text-secondary)] line-clamp-2">{entry.content}</p>
              <div className="flex gap-1 mt-1">
                {entry.tags.map((tag) => (
                  <span key={tag} className="text-[10px] px-1 py-0.5 bg-[var(--bg-primary)] rounded text-[var(--text-secondary)]">
                    {tag}
                  </span>
                ))}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 右侧详情 */}
      <div className="flex-1 p-6 overflow-y-auto">
        {selectedEntry ? (
          <div className="max-w-2xl">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-xl font-semibold">{selectedEntry.name}</h2>
              <span className={cn("px-2 py-0.5 text-xs rounded", layerColors[selectedEntry.scope])}>
                {layerLabels[selectedEntry.scope]}
              </span>
              {selectedEntry.pinned && <span>📌</span>}
            </div>
            {selectedEntry.repo_path && (
              <div className="text-sm text-[var(--text-secondary)] mb-4">
                仓库: <span className="font-mono">{selectedEntry.repo_path}</span>
              </div>
            )}
            <div className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)]">
              <pre className="whitespace-pre-wrap text-sm leading-relaxed">{selectedEntry.content}</pre>
            </div>
            <div className="flex gap-2 mt-4">
              {selectedEntry.tags.map((tag) => (
                <span key={tag} className="px-2 py-1 text-xs bg-[var(--bg-secondary)] rounded border border-[var(--border)]">
                  {tag}
                </span>
              ))}
            </div>
            <div className="mt-4 text-xs text-[var(--text-secondary)]">
              创建时间: {new Date(selectedEntry.created_at).toLocaleString()}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-[var(--text-secondary)]">
            <span className="text-4xl mb-4">📚</span>
            <p>选择一个知识条目查看详情</p>
            <p className="text-xs mt-2">三层体系: System(内置) / User(自定义) / Repo(仓库级)</p>
          </div>
        )}
      </div>
    </div>
  );
}
