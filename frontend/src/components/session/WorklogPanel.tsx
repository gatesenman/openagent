"use client";

import { useTranslations } from "next-intl";

interface WorklogEntry {
  id: string;
  type: string;
  title: string;
  detail?: string;
  timestamp: string;
  status?: "success" | "error" | "pending";
}

interface WorklogPanelProps {
  entries: WorklogEntry[];
}

const typeIcons: Record<string, string> = {
  "agent.thinking": "🧠",
  "agent.action": "⚡",
  "tool.call": "🔧",
  "tool.result": "📋",
  "file.write": "📝",
  "file.read": "📖",
  "sandbox.exec": "💻",
  "git.commit": "📦",
  "git.push": "🚀",
  "agent.error": "❌",
  "agent.complete": "✅",
};

const mockEntries: WorklogEntry[] = [
  {
    id: "1",
    type: "agent.thinking",
    title: "分析需求: 用户登录模块",
    detail: "解析用户输入, 确定需要创建的文件和依赖",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    status: "success",
  },
  {
    id: "2",
    type: "tool.call",
    title: "shell_exec: pip install bcrypt pyjwt",
    detail: "在沙箱中安装认证依赖",
    timestamp: new Date(Date.now() - 100000).toISOString(),
    status: "success",
  },
  {
    id: "3",
    type: "file.write",
    title: "创建 auth/models.py",
    detail: "定义 User 模型, 包含邮箱和密码哈希字段",
    timestamp: new Date(Date.now() - 80000).toISOString(),
    status: "success",
  },
  {
    id: "4",
    type: "file.write",
    title: "创建 auth/router.py",
    detail: "实现 /login 和 /register 端点",
    timestamp: new Date(Date.now() - 60000).toISOString(),
    status: "success",
  },
  {
    id: "5",
    type: "sandbox.exec",
    title: "运行测试: pytest tests/test_auth.py",
    detail: "执行 4 个测试用例",
    timestamp: new Date(Date.now() - 40000).toISOString(),
    status: "success",
  },
  {
    id: "6",
    type: "git.commit",
    title: "git commit -m 'feat: add auth module'",
    timestamp: new Date(Date.now() - 20000).toISOString(),
    status: "success",
  },
  {
    id: "7",
    type: "agent.thinking",
    title: "检查代码覆盖率...",
    timestamp: new Date().toISOString(),
    status: "pending",
  },
];

export function WorklogPanel({ entries }: WorklogPanelProps) {
  const t = useTranslations("session");
  const items = entries.length > 0 ? entries : mockEntries;

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="relative">
        {/* 时间线竖线 */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-[var(--border)]" />

        <div className="space-y-4">
          {items.map((entry) => (
            <div key={entry.id} className="relative flex items-start pl-10">
              {/* 时间线节点 */}
              <div
                className={`absolute left-2.5 w-3 h-3 rounded-full border-2 ${
                  entry.status === "error"
                    ? "bg-red-500 border-red-400"
                    : entry.status === "pending"
                    ? "bg-yellow-500 border-yellow-400 animate-pulse"
                    : "bg-green-500 border-green-400"
                }`}
              />

              <div className="flex-1 bg-[var(--bg-secondary)] rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm">
                    {typeIcons[entry.type] || "📌"}
                  </span>
                  <span className="text-sm font-medium text-[var(--text-primary)]">
                    {entry.title}
                  </span>
                </div>
                {entry.detail && (
                  <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    {entry.detail}
                  </p>
                )}
                <time className="mt-1 block text-xs text-[var(--text-secondary)] opacity-60">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </time>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
