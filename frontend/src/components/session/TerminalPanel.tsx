"use client";

import { useEffect, useRef, useState } from "react";

interface TerminalLine {
  type: "input" | "output" | "error";
  content: string;
  timestamp: string;
}

export function TerminalPanel({ sessionId }: { sessionId: string }) {
  const [lines, setLines] = useState<TerminalLine[]>([
    {
      type: "output",
      content: "OpenAgent Terminal - 沙箱虚拟环境",
      timestamp: new Date().toISOString(),
    },
    {
      type: "output",
      content: `Session: ${sessionId}`,
      timestamp: new Date().toISOString(),
    },
    {
      type: "input",
      content: "$ ls -la",
      timestamp: new Date().toISOString(),
    },
    {
      type: "output",
      content:
        "total 24\ndrwxr-xr-x  5 agent agent 4096 Jan  1 00:00 .\ndrwxr-xr-x  3 root  root  4096 Jan  1 00:00 ..\n-rw-r--r--  1 agent agent  220 Jan  1 00:00 .bashrc\ndrwxr-xr-x  2 agent agent 4096 Jan  1 00:00 workspace",
      timestamp: new Date().toISOString(),
    },
  ]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div className="h-full bg-black text-green-400 terminal overflow-y-auto p-4">
      {lines.map((line, i) => (
        <div key={i} className="mb-1">
          {line.type === "input" ? (
            <span className="text-cyan-400">{line.content}</span>
          ) : line.type === "error" ? (
            <span className="text-red-400">{line.content}</span>
          ) : (
            <span className="whitespace-pre-wrap">{line.content}</span>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
