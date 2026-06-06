"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

type ViewMode = "flow" | "dependencies" | "overview";

interface FlowStepData {
  step_number: number;
  title: string;
  description: string;
  source_file: string;
  source_lines: string;
  code_snippet: string;
  next_steps: number[];
}

const mockFlowSteps: FlowStepData[] = [
  {
    step_number: 1,
    title: "模块导入",
    description: "导入 FastAPI、Agent 引擎和沙箱管理器",
    source_file: "backend/app/main.py",
    source_lines: "1-18",
    code_snippet:
      'from fastapi import FastAPI\nfrom app.agent.react_engine import ReactEngine\nfrom app.sandbox.manager import sandbox_manager',
    next_steps: [2],
  },
  {
    step_number: 2,
    title: "Function: lifespan",
    description: "应用生命周期管理：初始化数据库和沙箱",
    source_file: "backend/app/main.py",
    source_lines: "27-37",
    code_snippet:
      "async def lifespan(app):\n    Base.metadata.create_all()\n    yield\n    await sandbox_manager.cleanup_all()",
    next_steps: [3],
  },
  {
    step_number: 3,
    title: "Class: ReactEngine",
    description: "ReAct 循环核心：Think → Act → Observe → Reflect",
    source_file: "backend/app/agent/react_engine.py",
    source_lines: "1-520",
    code_snippet:
      "class ReactEngine:\n    async def run(self, messages, session_id):\n        # Think → Act → Observe → Reflect loop\n        for i in range(self.max_iterations):\n            ...",
    next_steps: [4, 5],
  },
  {
    step_number: 4,
    title: "Function: exec_command",
    description: "在 Docker 沙箱中执行命令",
    source_file: "backend/app/sandbox/docker_sandbox.py",
    source_lines: "80-130",
    code_snippet:
      'async def exec_command(self, command, timeout=30):\n    proc = await asyncio.create_subprocess_exec(\n        "docker", "exec", self.container_name, "sh", "-c", command\n    )',
    next_steps: [],
  },
  {
    step_number: 5,
    title: "Function: generate_flow",
    description: "生成代码流程图（CodeMap 核心）",
    source_file: "backend/app/services/codemap/flow_generator.py",
    source_lines: "1-50",
    code_snippet:
      "class FlowGenerator:\n    async def generate_flow(self, entry_point, repo_path):\n        steps = self._generate_static(entry_point, repo_path)\n        return steps",
    next_steps: [],
  },
];

export default function CodeMapsPage() {
  const t = useTranslations("codemap");
  const [viewMode, setViewMode] = useState<ViewMode>("flow");

  return (
    <div className="flex flex-col h-full">
      {/* 顶部控制栏 */}
      <div className="p-4 border-b border-[var(--border)] flex items-center gap-4">
        <h2 className="text-lg font-semibold">{t("title")}</h2>
        <div className="flex gap-1 bg-[var(--bg-secondary)] rounded-lg p-1">
          {(["flow", "dependencies", "overview"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={cn(
                "px-3 py-1 rounded text-sm transition-colors",
                viewMode === mode
                  ? "bg-[var(--accent)] text-white"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              )}
            >
              {mode === "flow"
                ? t("codeFlow")
                : mode === "dependencies"
                  ? t("dependencyGraph")
                  : t("moduleOverview")}
            </button>
          ))}
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 overflow-y-auto p-6">
        {viewMode === "flow" && <FlowView steps={mockFlowSteps} />}
        {viewMode === "dependencies" && <DependencyView />}
        {viewMode === "overview" && <OverviewView />}
      </div>
    </div>
  );
}

function FlowView({ steps }: { steps: FlowStepData[] }) {
  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {steps.map((step) => (
        <div
          key={step.step_number}
          className="rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] overflow-hidden"
        >
          {/* 步骤头 */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border)]">
            <span className="w-7 h-7 rounded-full bg-[var(--accent)] flex items-center justify-center text-white text-sm font-bold">
              {step.step_number}
            </span>
            <div>
              <h3 className="font-semibold text-sm">{step.title}</h3>
              <p className="text-xs text-[var(--text-secondary)]">
                {step.description}
              </p>
            </div>
          </div>

          {/* 代码片段 */}
          <pre className="px-4 py-3 text-xs terminal overflow-x-auto">
            {step.code_snippet}
          </pre>

          {/* 源码位置 */}
          <div className="px-4 py-2 border-t border-[var(--border)] flex items-center justify-between text-xs text-[var(--text-secondary)]">
            <span>
              📄 {step.source_file}:{step.source_lines}
            </span>
            {step.next_steps.length > 0 && (
              <span>→ 步骤 {step.next_steps.join(", ")}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function DependencyView() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] p-6">
        <h3 className="text-lg font-semibold mb-4">依赖关系图</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-[var(--accent)]">main.py</span>
            <span className="text-[var(--text-secondary)]">→</span>
            <span>sessions.py, agents.py, tools.py, deepwiki.py, codemaps.py</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[var(--accent)]">sessions.py</span>
            <span className="text-[var(--text-secondary)]">→</span>
            <span>session_service.py → react_engine.py → sandbox_manager.py</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[var(--accent)]">deepwiki.py</span>
            <span className="text-[var(--text-secondary)]">→</span>
            <span>indexer.py → parser.py, symbol_extractor.py, embedding_service.py</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[var(--accent)]">codemaps.py</span>
            <span className="text-[var(--text-secondary)]">→</span>
            <span>analyzer.py, dependency_graph.py, flow_generator.py</span>
          </div>
        </div>
        <p className="mt-4 text-xs text-[var(--text-secondary)]">
          ✓ 无循环依赖
        </p>
      </div>
    </div>
  );
}

function OverviewView() {
  const modules = [
    { name: "sandbox", files: 4, symbols: 12, complexity: 8 },
    { name: "agent", files: 7, symbols: 25, complexity: 15 },
    { name: "services", files: 9, symbols: 18, complexity: 12 },
    { name: "api", files: 5, symbols: 15, complexity: 6 },
    { name: "models", files: 3, symbols: 8, complexity: 3 },
  ];

  return (
    <div className="max-w-3xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modules.map((mod) => (
          <div
            key={mod.name}
            className="rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] p-4"
          >
            <h3 className="font-semibold mb-2">{mod.name}</h3>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <span className="text-[var(--text-secondary)]">文件</span>
                <p className="text-lg font-bold">{mod.files}</p>
              </div>
              <div>
                <span className="text-[var(--text-secondary)]">符号</span>
                <p className="text-lg font-bold">{mod.symbols}</p>
              </div>
              <div>
                <span className="text-[var(--text-secondary)]">复杂度</span>
                <p className="text-lg font-bold">{mod.complexity}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
