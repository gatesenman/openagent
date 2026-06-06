"use client";

/**
 * 新建会话对话框 / New session dialog.
 * 选择运行模式、模型、平台后创建新会话。
 */

import { useState } from "react";

interface NewSessionDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    mode: string;
    model: string;
    platform: string;
    prompt: string;
  }) => void;
}

const MODES = [
  { value: "localhost", label: "Localhost", desc: "本地开发模式" },
  { value: "cascade", label: "Cascade", desc: "编辑器内模式" },
  { value: "cloud", label: "Cloud", desc: "云端虚拟机模式" },
];

const MODELS = [
  { value: "gpt-4o", label: "GPT-4o", provider: "OpenAI" },
  { value: "deepseek-chat", label: "DeepSeek Chat", provider: "DeepSeek" },
  { value: "qwen-plus", label: "Qwen Plus", provider: "阿里云" },
  { value: "claude-3-5-sonnet", label: "Claude 3.5", provider: "Anthropic" },
  { value: "llama3", label: "Llama 3", provider: "Ollama (本地)" },
];

const PLATFORMS = [
  { value: "linux", label: "Ubuntu 22.04" },
  { value: "windows", label: "Windows Server 2022" },
];

export default function NewSessionDialog({
  open,
  onClose,
  onSubmit,
}: NewSessionDialogProps) {
  const [title, setTitle] = useState("");
  const [mode, setMode] = useState("cloud");
  const [model, setModel] = useState("gpt-4o");
  const [platform, setPlatform] = useState("linux");
  const [prompt, setPrompt] = useState("");

  if (!open) return null;

  const handleSubmit = () => {
    onSubmit({
      title: title || "新会话",
      mode,
      model,
      platform,
      prompt,
    });
    setTitle("");
    setPrompt("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-lg rounded-xl border border-zinc-700 bg-zinc-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">创建新会话</h2>

        {/* 标题 */}
        <div className="mb-4">
          <label className="mb-1 block text-sm text-zinc-400">会话标题</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="描述你要完成的任务..."
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none"
          />
        </div>

        {/* 运行模式 */}
        <div className="mb-4">
          <label className="mb-2 block text-sm text-zinc-400">运行模式</label>
          <div className="grid grid-cols-3 gap-2">
            {MODES.map((m) => (
              <button
                key={m.value}
                onClick={() => setMode(m.value)}
                className={`rounded-lg border p-3 text-left transition ${
                  mode === m.value
                    ? "border-blue-500 bg-blue-500/10 text-blue-400"
                    : "border-zinc-700 bg-zinc-800 text-zinc-300 hover:border-zinc-600"
                }`}
              >
                <div className="text-sm font-medium">{m.label}</div>
                <div className="mt-1 text-xs text-zinc-500">{m.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* 模型选择 */}
        <div className="mb-4">
          <label className="mb-1 block text-sm text-zinc-400">AI 模型</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
          >
            {MODELS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label} ({m.provider})
              </option>
            ))}
          </select>
        </div>

        {/* 平台选择 */}
        <div className="mb-4">
          <label className="mb-1 block text-sm text-zinc-400">目标平台</label>
          <div className="grid grid-cols-2 gap-2">
            {PLATFORMS.map((p) => (
              <button
                key={p.value}
                onClick={() => setPlatform(p.value)}
                className={`rounded-lg border px-3 py-2 text-sm transition ${
                  platform === p.value
                    ? "border-blue-500 bg-blue-500/10 text-blue-400"
                    : "border-zinc-700 bg-zinc-800 text-zinc-300 hover:border-zinc-600"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* 初始提示 */}
        <div className="mb-6">
          <label className="mb-1 block text-sm text-zinc-400">
            初始指令（可选）
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="告诉 Agent 你想要完成什么..."
            rows={3}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none"
          />
        </div>

        {/* 按钮 */}
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-lg border border-zinc-700 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800"
          >
            取消
          </button>
          <button
            onClick={handleSubmit}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
          >
            创建会话
          </button>
        </div>
      </div>
    </div>
  );
}
