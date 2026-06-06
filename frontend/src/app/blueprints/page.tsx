"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface Blueprint {
  id: string;
  name: string;
  target: string;
  initialize: string;
  maintenance: string;
  knowledge: { name: string; contents: string }[];
}

export default function BlueprintsPage() {
  const t = useTranslations("blueprints");
  const [blueprints] = useState<Blueprint[]>([
    {
      id: "1",
      name: "Python + FastAPI",
      target: "template",
      initialize: "pip install uv\nuv venv .venv\nsource .venv/bin/activate",
      maintenance: "uv sync\npip install -e .",
      knowledge: [
        { name: "test", contents: "pytest tests/ -v" },
        { name: "lint", contents: "ruff check ." },
      ],
    },
    {
      id: "2",
      name: "Node.js + Next.js",
      target: "template",
      initialize: "corepack enable\npnpm install",
      maintenance: "pnpm install",
      knowledge: [
        { name: "test", contents: "pnpm test" },
        { name: "lint", contents: "pnpm lint" },
        { name: "startup", contents: "pnpm dev" },
      ],
    },
    {
      id: "3",
      name: "Rust + Cargo",
      target: "template",
      initialize: "rustup update stable",
      maintenance: "cargo fetch",
      knowledge: [
        { name: "test", contents: "cargo test" },
        { name: "lint", contents: "cargo clippy" },
      ],
    },
  ]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const selected = blueprints.find((b) => b.id === selectedId);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm">
          {t("create")}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {blueprints.map((bp) => (
          <button
            key={bp.id}
            onClick={() => setSelectedId(bp.id)}
            className={`text-left p-4 rounded-lg border transition ${
              selectedId === bp.id
                ? "border-[var(--accent)] bg-[var(--accent)]/10"
                : "border-[var(--border)] bg-[var(--bg-secondary)] hover:border-[var(--accent)]/50"
            }`}
          >
            <div className="font-medium mb-1">{bp.name}</div>
            <div className="text-xs text-[var(--text-secondary)]">
              {bp.knowledge.length} {t("knowledgeItems")}
            </div>
            <div className="mt-2 px-2 py-0.5 inline-block rounded-full text-xs bg-zinc-700 text-zinc-300">
              {bp.target}
            </div>
          </button>
        ))}
      </div>

      {selected && (
        <div className="bg-[var(--bg-secondary)] rounded-lg border border-[var(--border)] overflow-hidden">
          <div className="p-4 border-b border-[var(--border)]">
            <h2 className="font-semibold">{selected.name} — YAML {t("preview")}</h2>
          </div>
          <div className="p-4 space-y-4">
            <div>
              <div className="text-xs text-[var(--text-secondary)] mb-1 uppercase font-semibold">initialize</div>
              <pre className="bg-zinc-900 rounded p-3 text-sm text-green-400 font-mono overflow-x-auto">
                {selected.initialize}
              </pre>
            </div>
            <div>
              <div className="text-xs text-[var(--text-secondary)] mb-1 uppercase font-semibold">maintenance</div>
              <pre className="bg-zinc-900 rounded p-3 text-sm text-yellow-400 font-mono overflow-x-auto">
                {selected.maintenance}
              </pre>
            </div>
            <div>
              <div className="text-xs text-[var(--text-secondary)] mb-1 uppercase font-semibold">knowledge</div>
              <div className="space-y-2">
                {selected.knowledge.map((k) => (
                  <div key={k.name} className="bg-zinc-900 rounded p-3">
                    <span className="text-cyan-400 font-mono text-sm">{k.name}: </span>
                    <span className="text-zinc-300 font-mono text-sm">{k.contents}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
