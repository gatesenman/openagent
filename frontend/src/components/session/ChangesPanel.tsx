"use client";

/**
 * 变更面板 / Changes panel.
 * 显示 Agent 在沙箱中的代码变更（git diff 样式）。
 */

import { useState } from "react";

interface FileChange {
  path: string;
  status: "added" | "modified" | "deleted";
  additions: number;
  deletions: number;
  hunks?: DiffHunk[];
}

interface DiffHunk {
  header: string;
  lines: DiffLine[];
}

interface DiffLine {
  type: "add" | "remove" | "context";
  content: string;
  oldLineNumber?: number;
  newLineNumber?: number;
}

const statusColors = {
  added: "text-green-400",
  modified: "text-yellow-400",
  deleted: "text-red-400",
};

const statusLabels = {
  added: "新增",
  modified: "修改",
  deleted: "删除",
};

export function ChangesPanel() {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const mockChanges: FileChange[] = [
    {
      path: "src/components/Login.tsx",
      status: "added",
      additions: 45,
      deletions: 0,
      hunks: [
        {
          header: "@@ -0,0 +1,45 @@",
          lines: [
            { type: "add", content: 'import React from "react";', newLineNumber: 1 },
            { type: "add", content: "", newLineNumber: 2 },
            { type: "add", content: "export function Login() {", newLineNumber: 3 },
            { type: "add", content: "  const [email, setEmail] = useState('');", newLineNumber: 4 },
            { type: "add", content: "  return (", newLineNumber: 5 },
            { type: "add", content: '    <div className="login-form">', newLineNumber: 6 },
            { type: "add", content: "      <input value={email} />", newLineNumber: 7 },
            { type: "add", content: "    </div>", newLineNumber: 8 },
            { type: "add", content: "  );", newLineNumber: 9 },
            { type: "add", content: "}", newLineNumber: 10 },
          ],
        },
      ],
    },
    {
      path: "src/App.tsx",
      status: "modified",
      additions: 3,
      deletions: 1,
      hunks: [
        {
          header: "@@ -5,7 +5,9 @@",
          lines: [
            { type: "context", content: 'import { Header } from "./Header";', oldLineNumber: 5, newLineNumber: 5 },
            { type: "remove", content: 'import { Home } from "./Home";', oldLineNumber: 6 },
            { type: "add", content: 'import { Home } from "./Home";', newLineNumber: 6 },
            { type: "add", content: 'import { Login } from "./components/Login";', newLineNumber: 7 },
            { type: "add", content: 'import { AuthProvider } from "./auth";', newLineNumber: 8 },
            { type: "context", content: "", oldLineNumber: 7, newLineNumber: 9 },
          ],
        },
      ],
    },
    {
      path: "src/old-auth.ts",
      status: "deleted",
      additions: 0,
      deletions: 28,
    },
  ];

  const totalAdditions = mockChanges.reduce((s, c) => s + c.additions, 0);
  const totalDeletions = mockChanges.reduce((s, c) => s + c.deletions, 0);

  return (
    <div className="flex h-full">
      {/* 文件列表 */}
      <div className="w-64 border-r border-zinc-700 overflow-y-auto">
        <div className="p-3 border-b border-zinc-700">
          <div className="text-sm text-zinc-400">
            {mockChanges.length} 个文件变更
          </div>
          <div className="flex gap-3 mt-1 text-xs">
            <span className="text-green-400">+{totalAdditions}</span>
            <span className="text-red-400">-{totalDeletions}</span>
          </div>
        </div>

        {mockChanges.map((change) => (
          <button
            key={change.path}
            onClick={() => setSelectedFile(change.path)}
            className={`w-full px-3 py-2 text-left text-sm hover:bg-zinc-800 transition ${
              selectedFile === change.path ? "bg-zinc-800" : ""
            }`}
          >
            <div className="flex items-center gap-2">
              <span className={`text-xs font-mono ${statusColors[change.status]}`}>
                {change.status === "added" ? "A" : change.status === "deleted" ? "D" : "M"}
              </span>
              <span className="truncate text-zinc-300">
                {change.path.split("/").pop()}
              </span>
            </div>
            <div className="text-xs text-zinc-500 mt-0.5 pl-5">
              {change.path}
            </div>
          </button>
        ))}
      </div>

      {/* Diff 视图 */}
      <div className="flex-1 overflow-y-auto">
        {selectedFile ? (
          <div className="p-4">
            {mockChanges
              .filter((c) => c.path === selectedFile)
              .map((change) => (
                <div key={change.path}>
                  <div className="mb-3 flex items-center gap-2">
                    <span className={`text-sm font-medium ${statusColors[change.status]}`}>
                      [{statusLabels[change.status]}]
                    </span>
                    <span className="text-sm text-zinc-300 font-mono">{change.path}</span>
                  </div>
                  {change.hunks?.map((hunk, hi) => (
                    <div key={hi} className="mb-4 rounded border border-zinc-700 overflow-hidden">
                      <div className="bg-zinc-800 px-3 py-1 text-xs text-zinc-500 font-mono">
                        {hunk.header}
                      </div>
                      <div className="font-mono text-xs">
                        {hunk.lines.map((line, li) => (
                          <div
                            key={li}
                            className={`px-3 py-0.5 ${
                              line.type === "add"
                                ? "bg-green-900/20 text-green-300"
                                : line.type === "remove"
                                ? "bg-red-900/20 text-red-300"
                                : "text-zinc-400"
                            }`}
                          >
                            <span className="inline-block w-4 text-zinc-600 select-none">
                              {line.type === "add" ? "+" : line.type === "remove" ? "-" : " "}
                            </span>
                            {line.content}
                          </div>
                        ))}
                      </div>
                    </div>
                  )) || (
                    <div className="text-sm text-zinc-500 italic">
                      文件已{statusLabels[change.status]}（差异不可用）
                    </div>
                  )}
                </div>
              ))}
          </div>
        ) : (
          <div className="flex h-full items-center justify-center text-zinc-500 text-sm">
            选择文件查看差异
          </div>
        )}
      </div>
    </div>
  );
}
