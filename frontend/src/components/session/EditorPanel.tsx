"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

interface FileTab {
  path: string;
  content: string;
  language: string;
  modified: boolean;
}

export function EditorPanel({ sessionId }: { sessionId: string }) {
  const t = useTranslations("session");
  const [files] = useState<FileTab[]>([
    {
      path: "src/main.py",
      content: '"""OpenAgent main entry."""\n\nimport asyncio\n\n\nasync def main():\n    print("Hello from sandbox")\n\n\nif __name__ == "__main__":\n    asyncio.run(main())\n',
      language: "python",
      modified: false,
    },
  ]);
  const [activeFile, setActiveFile] = useState(0);
  const [lineNumbers] = useState(true);

  const currentFile = files[activeFile];
  const lines = currentFile?.content.split("\n") || [];

  return (
    <div className="flex flex-col h-full bg-[var(--bg-primary)]">
      {/* Tab bar */}
      <div className="flex items-center gap-0 border-b border-[var(--border)] bg-[var(--bg-secondary)]">
        {files.map((file, idx) => (
          <button
            key={file.path}
            onClick={() => setActiveFile(idx)}
            className={`px-3 py-1.5 text-xs border-r border-[var(--border)] flex items-center gap-1.5 ${
              idx === activeFile
                ? "bg-[var(--bg-primary)] text-[var(--text-primary)]"
                : "text-[var(--text-secondary)] hover:bg-white/5"
            }`}
          >
            <span className="text-blue-400">
              {file.language === "python" ? "🐍" : file.language === "typescript" ? "📘" : "📄"}
            </span>
            <span>{file.path.split("/").pop()}</span>
            {file.modified && <span className="w-1.5 h-1.5 rounded-full bg-white/50" />}
          </button>
        ))}
        <div className="flex-1" />
        <span className="text-xs text-[var(--text-secondary)] px-2">
          {currentFile?.language} | UTF-8 | LF
        </span>
      </div>

      {/* Editor area */}
      <div className="flex-1 overflow-auto font-mono text-sm">
        <div className="flex min-h-full">
          {/* Line numbers */}
          {lineNumbers && (
            <div className="flex flex-col items-end pr-3 pl-2 py-2 text-[var(--text-secondary)] select-none border-r border-[var(--border)] bg-[var(--bg-secondary)]">
              {lines.map((_, i) => (
                <div key={i} className="leading-6 text-xs opacity-50">
                  {i + 1}
                </div>
              ))}
            </div>
          )}

          {/* Code content */}
          <pre className="flex-1 p-2 whitespace-pre leading-6 text-xs">
            {lines.map((line, i) => (
              <div key={i} className="hover:bg-white/5 px-2">
                {colorize(line, currentFile?.language || "")}
              </div>
            ))}
          </pre>
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between px-3 py-1 text-xs text-[var(--text-secondary)] bg-[var(--bg-secondary)] border-t border-[var(--border)]">
        <div className="flex items-center gap-3">
          <span>Ln 1, Col 1</span>
          <span>Spaces: 4</span>
        </div>
        <div className="flex items-center gap-3">
          <span>{currentFile?.path}</span>
          <span className="text-green-400">Agent Editor (Read-only)</span>
        </div>
      </div>
    </div>
  );
}

function colorize(line: string, language: string): React.ReactNode {
  if (language !== "python") return line;

  const keywords = /\b(def|class|import|from|return|if|else|elif|async|await|for|in|while|try|except|with|as|None|True|False)\b/g;
  const strings = /("[^"]*"|'[^']*')/g;
  const comments = /(#.*$)/;

  const commentMatch = line.match(comments);
  if (commentMatch && line.trimStart().startsWith("#")) {
    return <span className="text-green-600">{line}</span>;
  }

  const parts: React.ReactNode[] = [];
  let lastIdx = 0;
  const combined = new RegExp(`(${keywords.source})|(${strings.source})|(${comments.source})`, "g");
  let match;

  while ((match = combined.exec(line)) !== null) {
    if (match.index > lastIdx) {
      parts.push(line.slice(lastIdx, match.index));
    }
    if (match[1]) {
      parts.push(<span key={match.index} className="text-purple-400">{match[0]}</span>);
    } else if (match[3]) {
      parts.push(<span key={match.index} className="text-amber-300">{match[0]}</span>);
    } else if (match[5]) {
      parts.push(<span key={match.index} className="text-green-600">{match[0]}</span>);
    }
    lastIdx = match.index + match[0].length;
  }
  if (lastIdx < line.length) {
    parts.push(line.slice(lastIdx));
  }
  return parts.length > 0 ? <>{parts}</> : line;
}
