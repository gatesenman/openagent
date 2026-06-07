"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import type { Message } from "@/lib/api";

interface ChatPanelProps {
  sessionId: string;
  messages: Message[];
  onSend: (content: string) => void;
}

export function ChatPanel({ sessionId, messages, onSend }: ChatPanelProps) {
  const t = useTranslations("session");
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((msg) => (
          <div key={msg.id} className="flex gap-2">
            {/* Avatar */}
            <div className={`w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5 text-[10px] font-bold ${
              msg.role === "user"
                ? "bg-[var(--accent)]/20 text-[var(--accent)]"
                : "bg-emerald-500/20 text-emerald-400"
            }`}>
              {msg.role === "user" ? "U" : "A"}
            </div>
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-[11px] font-medium text-[var(--text-secondary)]">
                  {msg.role === "user" ? "You" : "Agent"}
                </span>
                <span className="text-[10px] text-[var(--text-secondary)]/60">
                  {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className="text-[13px] leading-relaxed text-[var(--text-primary)] whitespace-pre-wrap">
                {msg.content}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="border-t border-[var(--border)] p-2">
        <div className="flex gap-1.5">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={t("placeholder")}
            className="flex-1 bg-[var(--surface)] border border-[var(--border)] rounded-md px-3 py-1.5 text-xs focus:outline-none focus:border-[var(--accent)]/40 text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="px-3 py-1.5 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-md text-xs font-medium disabled:opacity-30 transition-colors"
          >
            {t("send")}
          </button>
        </div>
      </div>
    </div>
  );
}
