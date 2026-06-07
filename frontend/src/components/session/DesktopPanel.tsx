"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface DesktopFrame {
  timestamp: number;
  type: "screenshot" | "stream";
  data: string;
}

export function DesktopPanel({ sessionId }: { sessionId?: string }) {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [resolution, setResolution] = useState("1920x1080");
  const [frames, setFrames] = useState<DesktopFrame[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);

  const connect = useCallback(async () => {
    setConnecting(true);
    try {
      await new Promise((r) => setTimeout(r, 1200));
      setConnected(true);
      setFrames([{ timestamp: Date.now(), type: "screenshot", data: "" }]);
    } catch {
      setConnected(false);
    } finally {
      setConnecting(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    setConnected(false);
    setFrames([]);
  }, []);

  useEffect(() => {
    return () => { disconnect(); };
  }, [disconnect]);

  if (!connected) {
    return (
      <div className="flex h-full flex-col items-center justify-center bg-[var(--bg-primary)] p-8">
        <div className="w-16 h-16 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border)] flex items-center justify-center mb-4">
          <svg className="w-7 h-7 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="2" y="3" width="20" height="14" rx="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
        </div>
        <h3 className="text-sm font-medium text-[var(--text-primary)] mb-1">Virtual Desktop</h3>
        <p className="text-[11px] text-[var(--text-secondary)] text-center max-w-xs mb-5">
          Connect to the sandbox virtual environment via noVNC. Watch Agent operate in real-time.
        </p>

        <div className="flex items-center gap-2 mb-4">
          <select
            value={resolution}
            onChange={(e) => setResolution(e.target.value)}
            className="bg-[var(--surface)] border border-[var(--border)] rounded-md px-2 py-1 text-[11px] text-[var(--text-secondary)]"
          >
            <option value="1920x1080">1920x1080</option>
            <option value="1280x720">1280x720</option>
            <option value="1024x768">1024x768</option>
          </select>
        </div>

        <button
          onClick={connect}
          disabled={connecting}
          className="px-5 py-1.5 bg-[var(--accent)] text-white rounded-md text-xs font-medium hover:bg-[var(--accent-hover)] disabled:opacity-40 transition-colors"
        >
          {connecting ? "Connecting..." : "Connect Desktop"}
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[#0a0a12]">
      {/* Toolbar */}
      <div className="h-[28px] flex items-center justify-between px-2 bg-[var(--bg-tertiary)] border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <span className="w-[5px] h-[5px] rounded-full bg-[var(--success)]" />
          <span className="text-[10px] text-[var(--text-secondary)]">Connected</span>
          <span className="text-[10px] text-[var(--text-secondary)]/50">{resolution}</span>
        </div>
        <div className="flex items-center gap-1">
          <ToolbarBtn onClick={() => setFrames(prev => [...prev, { timestamp: Date.now(), type: "screenshot", data: "" }])}>
            Capture
          </ToolbarBtn>
          <ToolbarBtn onClick={() => setIsRecording(!isRecording)} active={isRecording}>
            {isRecording ? "Stop" : "Record"}
          </ToolbarBtn>
          <ToolbarBtn onClick={disconnect} danger>
            Disconnect
          </ToolbarBtn>
        </div>
      </div>

      {/* Desktop canvas */}
      <div ref={canvasRef} className="flex-1 flex items-center justify-center cursor-crosshair">
        <div className="text-center">
          <svg className="w-12 h-12 text-[var(--text-secondary)]/20 mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
            <rect x="2" y="3" width="20" height="14" rx="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          <p className="text-[11px] text-[var(--text-secondary)]/40">
            Desktop stream connected - Agent operating in sandbox
          </p>
          {frames.length > 0 && (
            <p className="text-[10px] text-[var(--text-secondary)]/30 mt-1">
              {frames.length} frame(s) received
            </p>
          )}
          {isRecording && (
            <div className="mt-2 flex items-center justify-center gap-1 text-red-400 text-[10px]">
              <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
              Recording
            </div>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="h-[22px] px-2 bg-[var(--bg-tertiary)] border-t border-[var(--border)] text-[10px] text-[var(--text-secondary)]/50 flex items-center gap-4">
        <span>F11: Fullscreen</span>
        <span>Ctrl+Shift+S: Screenshot</span>
      </div>
    </div>
  );
}

function ToolbarBtn({ children, onClick, active, danger }: {
  children: React.ReactNode; onClick: () => void; active?: boolean; danger?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-[10px] px-2 py-0.5 rounded transition-colors ${
        danger ? "text-red-400 hover:bg-red-500/10" :
        active ? "bg-red-500/20 text-red-300" :
        "text-[var(--text-secondary)] hover:bg-white/[0.04]"
      }`}
    >
      {children}
    </button>
  );
}
