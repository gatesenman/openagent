"use client";

import { useTranslations } from "next-intl";

export default function OnboardingPage() {
  const t = useTranslations("onboarding");

  const steps = [
    { id: "welcome", icon: "👋", status: "completed" },
    { id: "choose_mode", icon: "🔧", status: "completed" },
    { id: "connect_repo", icon: "📦", status: "current" },
    { id: "configure_llm", icon: "🤖", status: "pending" },
    { id: "first_session", icon: "💬", status: "pending" },
    { id: "explore_deepwiki", icon: "📚", status: "pending" },
    { id: "explore_codemap", icon: "🗺️", status: "pending" },
  ];

  const sampleProjects = [
    {
      id: "hello-fastapi",
      name: "Hello FastAPI",
      lang: "Python",
      difficulty: t("beginner"),
      time: "5 min",
      color: "bg-green-500/20 text-green-400",
    },
    {
      id: "react-todo",
      name: "React Todo App",
      lang: "TypeScript",
      difficulty: t("beginner"),
      time: "10 min",
      color: "bg-blue-500/20 text-blue-400",
    },
    {
      id: "fullstack-blog",
      name: t("fullstackBlog"),
      lang: "Fullstack",
      difficulty: t("intermediate"),
      time: "30 min",
      color: "bg-purple-500/20 text-purple-400",
    },
    {
      id: "cli-tool",
      name: t("cliTool"),
      lang: "Python",
      difficulty: t("intermediate"),
      time: "15 min",
      color: "bg-orange-500/20 text-orange-400",
    },
  ];

  const promptTemplates = [
    { id: "bug-fix", name: t("fixBug"), icon: "🐛", category: "debug" },
    { id: "add-feature", name: t("addFeature"), icon: "✨", category: "dev" },
    { id: "refactor", name: t("refactorCode"), icon: "♻️", category: "refactor" },
    { id: "write-tests", name: t("writeTests"), icon: "🧪", category: "test" },
    { id: "code-review", name: t("codeReview"), icon: "👀", category: "review" },
    { id: "api-design", name: t("apiDesign"), icon: "📐", category: "design" },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">{t("title")}</h1>
      <p className="text-[var(--text-secondary)] mb-8">{t("subtitle")}</p>

      {/* 引导步骤 */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)] mb-8">
        <h2 className="text-lg font-semibold mb-4">{t("stepsTitle")}</h2>
        <div className="space-y-3">
          {steps.map((step, i) => (
            <div
              key={step.id}
              className={`flex items-center gap-4 p-3 rounded-lg ${
                step.status === "current"
                  ? "bg-[var(--accent)]/10 border border-[var(--accent)]/30"
                  : step.status === "completed"
                  ? "opacity-60"
                  : ""
              }`}
            >
              <span className="text-xl w-8 text-center">
                {step.status === "completed" ? "✅" : step.icon}
              </span>
              <div className="flex-1">
                <div className="font-medium">{t(`step_${step.id}`)}</div>
                <div className="text-xs text-[var(--text-secondary)]">
                  {t(`step_${step.id}_desc`)}
                </div>
              </div>
              <span className="text-xs px-2 py-1 rounded-full bg-[var(--bg-primary)]">
                {i + 1}/7
              </span>
            </div>
          ))}
        </div>
        <div className="mt-4 flex gap-3">
          <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm font-medium">
            {t("continueSetup")}
          </button>
          <button className="px-4 py-2 border border-[var(--border)] rounded-lg text-sm text-[var(--text-secondary)]">
            {t("skipOnboarding")}
          </button>
        </div>
      </div>

      {/* 示例项目 */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">{t("sampleProjects")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sampleProjects.map((proj) => (
            <div
              key={proj.id}
              className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] hover:border-[var(--accent)]/50 cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{proj.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${proj.color}`}>
                  {proj.lang}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)]">
                <span>{proj.difficulty}</span>
                <span>·</span>
                <span>{proj.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Prompt 模板 */}
      <div>
        <h2 className="text-lg font-semibold mb-4">{t("promptTemplates")}</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {promptTemplates.map((tpl) => (
            <div
              key={tpl.id}
              className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] hover:border-[var(--accent)]/50 cursor-pointer transition-colors text-center"
            >
              <div className="text-2xl mb-2">{tpl.icon}</div>
              <div className="text-sm font-medium">{tpl.name}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
