"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

interface PlaybookStep {
  instruction: string;
  tool_hint?: string;
  validation?: string;
}

interface Playbook {
  id: string;
  name: string;
  description: string;
  category: "builtin" | "custom";
  steps: PlaybookStep[];
  tags: string[];
}

const mockPlaybooks: Playbook[] = [
  {
    id: "1",
    name: "code-review",
    description: "对指定 PR 或代码文件进行全面审查，包含安全性、性能、可维护性评估",
    category: "builtin",
    steps: [
      { instruction: "读取目标代码文件或 PR diff", tool_hint: "file_read / git_ops" },
      { instruction: "分析代码结构和依赖关系", tool_hint: "search_code" },
      { instruction: "检查安全漏洞（SQL注入、XSS、敏感信息泄露）", validation: "无高危安全问题" },
      { instruction: "评估性能瓶颈（N+1查询、内存泄漏、复杂度）", validation: "无P0性能问题" },
      { instruction: "检查代码规范和最佳实践", validation: "符合项目 lint 规则" },
      { instruction: "生成评审报告，包含改进建议和风险评级" },
    ],
    tags: ["审查", "安全", "质量"],
  },
  {
    id: "2",
    name: "bug-fix",
    description: "诊断并修复 Bug：复现 → 定位 → 修复 → 测试 → PR",
    category: "builtin",
    steps: [
      { instruction: "理解 Bug 描述，确定复现步骤" },
      { instruction: "在沙箱中复现 Bug", tool_hint: "shell_exec" },
      { instruction: "分析错误日志和堆栈", tool_hint: "search_code" },
      { instruction: "定位根因代码", tool_hint: "file_read / search_code" },
      { instruction: "编写修复代码", tool_hint: "file_write", validation: "修复通过原始复现步骤" },
      { instruction: "编写回归测试", tool_hint: "file_write / shell_exec" },
      { instruction: "提交 PR", tool_hint: "git_ops" },
    ],
    tags: ["修复", "调试"],
  },
  {
    id: "3",
    name: "feature-impl",
    description: "端到端功能开发：需求分析 → 设计 → 编码 → 测试 → 部署",
    category: "builtin",
    steps: [
      { instruction: "分析需求，拆解任务" },
      { instruction: "设计技术方案（API接口/数据模型/组件结构）" },
      { instruction: "创建代码骨架", tool_hint: "file_write" },
      { instruction: "实现核心逻辑", tool_hint: "file_write" },
      { instruction: "编写单元测试", tool_hint: "file_write" },
      { instruction: "运行测试", tool_hint: "shell_exec", validation: "所有测试通过" },
      { instruction: "代码自审", validation: "通过 lint 检查" },
      { instruction: "提交 PR 并描述变更", tool_hint: "git_ops" },
    ],
    tags: ["功能", "开发"],
  },
  {
    id: "4",
    name: "test-gen",
    description: "自动生成测试：分析代码 → 生成单元/集成/E2E测试 → 检查覆盖率",
    category: "builtin",
    steps: [
      { instruction: "分析目标代码的函数签名和逻辑分支" },
      { instruction: "生成单元测试（正常/边界/异常用例）", tool_hint: "file_write" },
      { instruction: "生成集成测试（API端点/服务交互）", tool_hint: "file_write" },
      { instruction: "运行测试并检查覆盖率", tool_hint: "shell_exec", validation: "覆盖率 > 80%" },
    ],
    tags: ["测试", "质量"],
  },
  {
    id: "5",
    name: "refactor",
    description: "代码重构：识别坏味道 → 安全重构 → 验证行为不变",
    category: "builtin",
    steps: [
      { instruction: "分析代码度量（复杂度/重复/耦合）", tool_hint: "search_code" },
      { instruction: "识别重构点（长函数/大类/深嵌套）" },
      { instruction: "确认现有测试覆盖" },
      { instruction: "逐步重构（每步保持可编译）", tool_hint: "file_write", validation: "测试通过" },
      { instruction: "验证行为不变", tool_hint: "shell_exec" },
    ],
    tags: ["重构", "质量"],
  },
  {
    id: "6",
    name: "deploy",
    description: "部署流程：构建 → 测试 → 镜像 → 部署 → 健康检查",
    category: "builtin",
    steps: [
      { instruction: "运行完整测试套件", tool_hint: "shell_exec", validation: "所有测试通过" },
      { instruction: "构建项目", tool_hint: "shell_exec" },
      { instruction: "构建 Docker 镜像", tool_hint: "shell_exec" },
      { instruction: "推送到 Registry", tool_hint: "shell_exec" },
      { instruction: "部署到目标环境", tool_hint: "shell_exec" },
      { instruction: "执行健康检查", tool_hint: "shell_exec", validation: "健康检查通过" },
    ],
    tags: ["部署", "运维"],
  },
];

export default function PlaybooksPage() {
  const t = useTranslations("nav");
  const [selectedPlaybook, setSelectedPlaybook] = useState<Playbook | null>(null);

  return (
    <div className="flex h-full">
      {/* 列表 */}
      <div className="w-80 border-r border-[var(--border)] flex flex-col">
        <div className="p-4 border-b border-[var(--border)]">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">{t("playbooks")}</h2>
            <button className="px-3 py-1 text-xs bg-[var(--accent)] text-white rounded hover:opacity-90">
              + 创建
            </button>
          </div>
          <p className="text-xs text-[var(--text-secondary)] mt-1">
            可复用的 Agent 任务模板
          </p>
        </div>

        <div className="flex-1 overflow-y-auto">
          {mockPlaybooks.map((pb) => (
            <button
              key={pb.id}
              onClick={() => setSelectedPlaybook(pb)}
              className={cn(
                "w-full text-left px-4 py-3 border-b border-[var(--border)] hover:bg-[var(--bg-secondary)] transition-colors",
                selectedPlaybook?.id === pb.id && "bg-[var(--bg-secondary)]"
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium">{pb.name}</span>
                <span className={cn(
                  "px-1.5 py-0.5 text-[10px] rounded",
                  pb.category === "builtin"
                    ? "bg-blue-500/20 text-blue-400"
                    : "bg-green-500/20 text-green-400"
                )}>
                  {pb.category === "builtin" ? "内置" : "自定义"}
                </span>
              </div>
              <p className="text-xs text-[var(--text-secondary)] line-clamp-2">{pb.description}</p>
              <div className="flex gap-1 mt-1.5">
                {pb.tags.map((tag) => (
                  <span key={tag} className="text-[10px] px-1 py-0.5 bg-[var(--bg-primary)] rounded text-[var(--text-secondary)]">
                    {tag}
                  </span>
                ))}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 详情 */}
      <div className="flex-1 p-6 overflow-y-auto">
        {selectedPlaybook ? (
          <div className="max-w-3xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold">{selectedPlaybook.name}</h2>
                <p className="text-sm text-[var(--text-secondary)] mt-1">{selectedPlaybook.description}</p>
              </div>
              <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 text-sm font-medium">
                执行此模板
              </button>
            </div>

            {/* 步骤列表 */}
            <div className="space-y-3 mt-6">
              <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                执行步骤 ({selectedPlaybook.steps.length} 步)
              </h3>
              {selectedPlaybook.steps.map((step, i) => (
                <div
                  key={i}
                  className="flex gap-4 bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)]"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--accent)]/20 text-[var(--accent)] flex items-center justify-center text-sm font-bold">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm">{step.instruction}</p>
                    <div className="flex gap-3 mt-2">
                      {step.tool_hint && (
                        <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded font-mono">
                          {step.tool_hint}
                        </span>
                      )}
                      {step.validation && (
                        <span className="text-[10px] px-1.5 py-0.5 bg-green-500/10 text-green-400 rounded">
                          验证: {step.validation}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-[var(--text-secondary)]">
            <span className="text-4xl mb-4">📋</span>
            <p>选择一个 Playbook 查看详情</p>
            <p className="text-xs mt-2">6 个内置模板 + 自定义模板支持</p>
          </div>
        )}
      </div>
    </div>
  );
}
