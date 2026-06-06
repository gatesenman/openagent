"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface SymbolItem {
  name: string;
  kind: string;
  file_path: string;
  signature: string;
}

const mockSymbols: SymbolItem[] = [
  {
    name: "ReactEngine",
    kind: "class",
    file_path: "backend/app/agent/react_engine.py",
    signature: "class ReactEngine",
  },
  {
    name: "DockerSandbox",
    kind: "class",
    file_path: "backend/app/sandbox/docker_sandbox.py",
    signature: "class DockerSandbox(BaseSandbox)",
  },
  {
    name: "SessionService",
    kind: "class",
    file_path: "backend/app/services/session_service.py",
    signature: "class SessionService",
  },
  {
    name: "CodeParser",
    kind: "class",
    file_path: "backend/app/services/deepwiki/parser.py",
    signature: "class CodeParser",
  },
  {
    name: "FlowGenerator",
    kind: "class",
    file_path: "backend/app/services/codemap/flow_generator.py",
    signature: "class FlowGenerator",
  },
];

const mockDoc = {
  definition:
    "`ReactEngine` 是 OpenAgent 的核心 Agent 引擎，实现 ReAct（Reasoning + Acting）循环。每轮循环经历 Think → Act → Observe → Reflect 四个阶段。",
  example_usages: [
    '```python\nengine = ReactEngine(sandbox=sandbox, llm_client=client, model="gpt-4o")\nasync for event in engine.run(messages, session_id="abc"):\n    print(event.type, event.data)\n```',
  ],
  notes: [
    "最大迭代次数默认为 50 次，连续 3 次错误会自动切换策略",
    "所有工具调用在沙箱虚拟环境中执行，确保隔离性",
  ],
  see_also: ["BaseSandbox", "ContextManager", "OutputValidator"],
  follow_up_questions: [
    "ReAct 循环中如何处理工具调用超时？",
    "如何添加自定义工具到 Agent 引擎？",
    "上下文窗口管理策略是什么？",
  ],
};

export default function DeepWikiPage() {
  const t = useTranslations("deepwiki");
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(
    "ReactEngine"
  );
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = mockSymbols.filter(
    (s) =>
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.file_path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex h-full">
      {/* 左侧符号列表 */}
      <div className="w-80 border-r border-[var(--border)] flex flex-col">
        <div className="p-4 border-b border-[var(--border)]">
          <h2 className="text-lg font-semibold mb-2">{t("title")}</h2>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t("searchSymbols")}
            className="w-full bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[var(--accent)]"
          />
        </div>
        <div className="flex-1 overflow-y-auto">
          {filtered.map((sym) => (
            <button
              key={sym.name}
              onClick={() => setSelectedSymbol(sym.name)}
              className={`w-full px-4 py-3 text-left border-b border-[var(--border)] transition-colors ${
                selectedSymbol === sym.name
                  ? "bg-[var(--accent)]/10"
                  : "hover:bg-white/5"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs px-1.5 py-0.5 rounded bg-[var(--accent)]/20 text-[var(--accent)]">
                  {sym.kind}
                </span>
                <span className="font-medium text-sm">{sym.name}</span>
              </div>
              <p className="text-xs text-[var(--text-secondary)] truncate">
                {sym.file_path}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* 右侧文档展示（5段式） */}
      <div className="flex-1 overflow-y-auto p-6">
        {selectedSymbol ? (
          <div className="max-w-3xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold">{selectedSymbol}</h1>

            {/* Definition */}
            <section>
              <h2 className="text-lg font-semibold text-[var(--accent)] mb-2">
                {t("sections.definition")}
              </h2>
              <p className="text-sm leading-relaxed">{mockDoc.definition}</p>
            </section>

            {/* Example Usages */}
            <section>
              <h2 className="text-lg font-semibold text-[var(--accent)] mb-2">
                {t("sections.exampleUsages")}
              </h2>
              {mockDoc.example_usages.map((example, i) => (
                <pre
                  key={i}
                  className="bg-[var(--bg-secondary)] rounded-lg p-4 text-xs terminal overflow-x-auto"
                >
                  {example}
                </pre>
              ))}
            </section>

            {/* Notes */}
            <section>
              <h2 className="text-lg font-semibold text-[var(--accent)] mb-2">
                {t("sections.notes")}
              </h2>
              <ul className="space-y-1">
                {mockDoc.notes.map((note, i) => (
                  <li
                    key={i}
                    className="text-sm text-[var(--text-secondary)] flex items-start gap-2"
                  >
                    <span className="text-[var(--warning)]">•</span>
                    {note}
                  </li>
                ))}
              </ul>
            </section>

            {/* See Also */}
            <section>
              <h2 className="text-lg font-semibold text-[var(--accent)] mb-2">
                {t("sections.seeAlso")}
              </h2>
              <div className="flex flex-wrap gap-2">
                {mockDoc.see_also.map((ref) => (
                  <span
                    key={ref}
                    className="text-sm px-3 py-1 rounded-full bg-[var(--bg-secondary)] border border-[var(--border)] cursor-pointer hover:border-[var(--accent)]"
                  >
                    {ref}
                  </span>
                ))}
              </div>
            </section>

            {/* Follow-up Questions */}
            <section>
              <h2 className="text-lg font-semibold text-[var(--accent)] mb-2">
                {t("sections.followUp")}
              </h2>
              <div className="space-y-2">
                {mockDoc.follow_up_questions.map((q, i) => (
                  <button
                    key={i}
                    className="block w-full text-left text-sm px-4 py-2 rounded-lg bg-[var(--bg-secondary)] border border-[var(--border)] hover:border-[var(--accent)] transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </section>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-[var(--text-secondary)]">
            {t("description")}
          </div>
        )}
      </div>
    </div>
  );
}
