"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { ChatPanel } from "./ChatPanel";
import { WorklogPanel } from "./WorklogPanel";
import { TerminalPanel } from "./TerminalPanel";
import type { Message } from "@/lib/api";

const tabs = ["chat", "worklog", "terminal", "changes", "desktop"] as const;
type TabKey = (typeof tabs)[number];

interface SessionDetailProps {
  sessionId: string;
}

export function SessionDetail({ sessionId }: SessionDetailProps) {
  const t = useTranslations("session");
  const [activeTab, setActiveTab] = useState<TabKey>("chat");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      session_id: sessionId,
      role: "user",
      content: "帮我实现一个用户登录模块，包含邮箱和密码验证",
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      session_id: sessionId,
      role: "assistant",
      content:
        "好的，我来帮你实现用户登录模块。我会在沙箱中执行以下步骤：\n\n1. 创建用户模型\n2. 实现登录API\n3. 添加邮箱和密码验证\n4. 编写测试\n\n正在开始...",
      created_at: new Date().toISOString(),
    },
  ]);

  const handleSend = (content: string) => {
    const newMsg: Message = {
      id: messages.length + 1,
      session_id: sessionId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
    setMessages([...messages, newMsg]);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Tab 栏 */}
      <div className="flex border-b border-[var(--border)] bg-[var(--bg-secondary)]">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
              activeTab === tab
                ? "border-[var(--accent)] text-[var(--accent)]"
                : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            )}
          >
            {t(`tabs.${tab}`)}
          </button>
        ))}
      </div>

      {/* Tab 内容 */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "chat" && (
          <ChatPanel
            sessionId={sessionId}
            messages={messages}
            onSend={handleSend}
          />
        )}
        {activeTab === "worklog" && <WorklogPanel entries={[]} />}
        {activeTab === "terminal" && (
          <TerminalPanel sessionId={sessionId} />
        )}
        {activeTab === "changes" && (
          <div className="flex items-center justify-center h-full text-[var(--text-secondary)]">
            暂无代码变更
          </div>
        )}
        {activeTab === "desktop" && (
          <div className="flex items-center justify-center h-full text-[var(--text-secondary)]">
            桌面流（VNC）将在 Phase 2 实现
          </div>
        )}
      </div>
    </div>
  );
}
