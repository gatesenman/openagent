"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { ChangesPanel } from "./ChangesPanel";
import { ChatPanel } from "./ChatPanel";
import { DesktopPanel } from "./DesktopPanel";
import { EditorPanel } from "./EditorPanel";
import { WorklogPanel } from "./WorklogPanel";
import { TerminalPanel } from "./TerminalPanel";
import type { Message } from "@/lib/api";

const rightTabs = ["desktop", "changes", "worklog", "shell", "ide", "agents"] as const;
type RightTab = (typeof rightTabs)[number];

interface SessionDetailProps {
  sessionId: string;
}

export function SessionDetail({ sessionId }: SessionDetailProps) {
  const t = useTranslations("session");
  const [activeRightTab, setActiveRightTab] = useState<RightTab>("desktop");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      session_id: sessionId,
      role: "user",
      content: "Help me implement a user login module with email and password validation",
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      session_id: sessionId,
      role: "assistant",
      content:
        "I'll implement the user login module in the sandbox environment.\n\n**Plan:**\n1. Create user model with email/password fields\n2. Implement login API endpoint\n3. Add validation middleware\n4. Write unit tests\n\nExecuting in sandbox...",
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
    <div className="flex h-full">
      {/* Left: Chat conversation */}
      <div className="w-[45%] min-w-[360px] border-r border-[var(--border)] flex flex-col">
        {/* Session header bar */}
        <div className="h-[32px] flex items-center justify-between px-3 bg-[var(--bg-tertiary)] border-b border-[var(--border)]">
          <div className="flex items-center gap-2">
            <span className="w-[6px] h-[6px] rounded-full bg-[var(--success)]" />
            <span className="text-[11px] font-medium text-[var(--text-secondary)] uppercase tracking-wider">Session</span>
            <span className="text-[10px] font-mono text-[var(--text-secondary)]">
              {sessionId.slice(0, 8)}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--success)]/10 text-[var(--success)] font-medium">
              Running
            </span>
          </div>
        </div>
        <div className="flex-1 overflow-hidden">
          <ChatPanel
            sessionId={sessionId}
            messages={messages}
            onSend={handleSend}
          />
        </div>
      </div>

      {/* Right: Tabbed panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Tab bar */}
        <div className="h-[32px] flex items-center bg-[var(--bg-tertiary)] border-b border-[var(--border)] px-1">
          {rightTabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveRightTab(tab)}
              className={cn(
                "tab-btn rounded-sm",
                activeRightTab === tab
                  ? "bg-[var(--bg-primary)] text-[var(--text-primary)] shadow-sm"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              )}
            >
              {t(`tabs.${tab}`)}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-hidden">
          {activeRightTab === "desktop" && <DesktopPanel sessionId={sessionId} />}
          {activeRightTab === "changes" && <ChangesPanel />}
          {activeRightTab === "worklog" && <WorklogPanel entries={[]} />}
          {activeRightTab === "shell" && <TerminalPanel sessionId={sessionId} />}
          {activeRightTab === "ide" && <EditorPanel sessionId={sessionId} />}
          {activeRightTab === "agents" && <AgentsPanel />}
        </div>
      </div>
    </div>
  );
}

function AgentsPanel() {
  const agents = [
    { id: "main", name: "Main Agent", status: "running", model: "GPT-4o", step: "Executing shell_exec" },
    { id: "sub-1", name: "Code Generator", status: "idle", model: "DeepSeek Coder", step: "Waiting" },
    { id: "sub-2", name: "Test Writer", status: "pending", model: "Claude Sonnet", step: "Queued" },
  ];

  return (
    <div className="h-full flex flex-col">
      <div className="panel-header">Active Agents</div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="bg-[var(--surface)] rounded-md p-3 border border-[var(--border)]"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-medium">{agent.name}</span>
              <span className={cn(
                "text-[10px] px-1.5 py-0.5 rounded font-medium",
                agent.status === "running" ? "bg-[var(--success)]/10 text-[var(--success)]" :
                agent.status === "idle" ? "bg-zinc-500/10 text-zinc-400" :
                "bg-[var(--warning)]/10 text-[var(--warning)]"
              )}>
                {agent.status}
              </span>
            </div>
            <div className="text-[10px] text-[var(--text-secondary)] space-y-0.5">
              <div>Model: <span className="text-[var(--text-primary)]">{agent.model}</span></div>
              <div>Step: <span className="font-mono text-[var(--text-primary)]">{agent.step}</span></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
