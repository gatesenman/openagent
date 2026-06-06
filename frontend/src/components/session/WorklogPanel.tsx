"use client";

import { cn } from "@/lib/utils";

interface WorklogEntry {
  id: string;
  type: string;
  title: string;
  content?: string;
  timestamp: string;
  duration_ms?: number;
}

const typeIcons: Record<string, string> = {
  think: "🤔",
  tool_call: "🔧",
  tool_result: "📋",
  code_edit: "📝",
  shell_exec: "💻",
  file_read: "📖",
  search: "🔍",
  error: "❌",
  plan_update: "📋",
};

const typeColors: Record<string, string> = {
  think: "border-blue-500/30",
  tool_call: "border-indigo-500/30",
  tool_result: "border-green-500/30",
  code_edit: "border-yellow-500/30",
  shell_exec: "border-purple-500/30",
  error: "border-red-500/30",
};

export function WorklogPanel({ entries }: { entries: WorklogEntry[] }) {
  // Mock 数据
  const mockEntries: WorklogEntry[] = entries.length
    ? entries
    : [
        {
          id: "1",
          type: "think",
          title: "分析需求",
          content: "正在分析用户需求，制定开发计划...",
          timestamp: new Date().toISOString(),
        },
        {
          id: "2",
          type: "shell_exec",
          title: "创建项目目录",
          content: "mkdir -p src/components",
          timestamp: new Date().toISOString(),
          duration_ms: 120,
        },
        {
          id: "3",
          type: "code_edit",
          title: "创建组件文件",
          content: "src/components/Login.tsx",
          timestamp: new Date().toISOString(),
          duration_ms: 450,
        },
        {
          id: "4",
          type: "tool_call",
          title: "运行测试",
          content: "npm test -- --watchAll=false",
          timestamp: new Date().toISOString(),
          duration_ms: 3200,
        },
      ];

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="relative">
        {/* 时间线 */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-[var(--border)]" />

        <div className="space-y-3">
          {mockEntries.map((entry) => (
            <div key={entry.id} className="relative pl-10">
              {/* 时间线节点 */}
              <div className="absolute left-2.5 top-2 w-3 h-3 rounded-full bg-[var(--bg-secondary)] border-2 border-[var(--accent)]" />

              <div
                className={cn(
                  "rounded-lg border bg-[var(--bg-secondary)] p-3",
                  typeColors[entry.type] || "border-[var(--border)]"
                )}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">
                    {typeIcons[entry.type] || "📌"}
                  </span>
                  <span className="font-medium text-sm">{entry.title}</span>
                  {entry.duration_ms && (
                    <span className="text-xs text-[var(--text-secondary)] ml-auto">
                      {entry.duration_ms}ms
                    </span>
                  )}
                </div>
                {entry.content && (
                  <p className="text-xs text-[var(--text-secondary)] terminal truncate">
                    {entry.content}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
