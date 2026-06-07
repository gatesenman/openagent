"use client";

import { useState } from "react";

export default function AskPage() {
  const [input, setInput] = useState("");

  return (
    <div className="flex flex-col items-center justify-center h-full px-8">
      <div className="max-w-2xl w-full">
        <h1 className="text-2xl font-bold mb-2 text-center">Ask</h1>
        <p className="text-sm text-[var(--text-secondary)] text-center mb-6">
          Ask questions about your codebase. Agent answers from indexed knowledge.
        </p>

        <div className="relative mb-6">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your code..."
            rows={3}
            className="w-full bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-[var(--accent)]"
          />
          <button className="absolute bottom-3 right-3 px-4 py-1.5 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-sm rounded-lg">
            Ask
          </button>
        </div>

        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase">Suggested Questions</h3>
          {[
            "How does the authentication flow work?",
            "What are the main API endpoints?",
            "Explain the database schema",
            "Where is error handling implemented?",
          ].map((q) => (
            <button
              key={q}
              onClick={() => setInput(q)}
              className="w-full text-left px-4 py-2 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] text-sm hover:border-[var(--accent)]/50 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
