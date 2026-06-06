"use client";

import { useState, useEffect, useRef, useCallback } from "react";

/**
 * 桌面面板 / Desktop panel.
 *
 * Phase 1: noVNC WebSocket 连接骨架 + 截屏显示
 * Phase 2: 完整 VNC/noVNC 集成 + KVM 虚拟机桌面
 */

interface DesktopFrame {
  timestamp: number;
  type: "screenshot" | "stream";
  data: string; // base64 image or URL
}

export function DesktopPanel({ sessionId }: { sessionId?: string }) {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [resolution, setResolution] = useState("1920x1080");
  const [frames, setFrames] = useState<DesktopFrame[]>([]);
  const [quality, setQuality] = useState(80);
  const [isRecording, setIsRecording] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);

  const connect = useCallback(async () => {
    setConnecting(true);
    try {
      // Phase 1: 模拟连接流程
      await new Promise((r) => setTimeout(r, 1500));
      setConnected(true);

      // 模拟接收桌面帧
      setFrames([{
        timestamp: Date.now(),
        type: "screenshot",
        data: "",
      }]);
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

  const takeScreenshot = useCallback(async () => {
    if (!sessionId) return;
    setFrames((prev) => [
      ...prev,
      { timestamp: Date.now(), type: "screenshot", data: "" },
    ]);
  }, [sessionId]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  if (!connected) {
    return (
      <div className="flex h-full flex-col items-center justify-center bg-zinc-950 p-8">
        <div className="mb-4 text-6xl">🖥️</div>
        <h3 className="mb-2 text-lg font-semibold text-white">远程桌面</h3>
        <p className="mb-4 max-w-md text-center text-sm text-zinc-400">
          通过 noVNC 连接沙箱虚拟环境的桌面，实时观看 Agent 的 GUI 操作。
        </p>

        <div className="flex items-center gap-3 mb-4">
          <select
            value={resolution}
            onChange={(e) => setResolution(e.target.value)}
            className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-sm text-zinc-300"
          >
            <option value="1920x1080">1920x1080 (FHD)</option>
            <option value="1280x720">1280x720 (HD)</option>
            <option value="1024x768">1024x768</option>
          </select>
          <input
            type="range"
            min={20}
            max={100}
            value={quality}
            onChange={(e) => setQuality(Number(e.target.value))}
            className="w-20"
          />
          <span className="text-xs text-zinc-500">Q:{quality}%</span>
        </div>

        <button
          onClick={connect}
          disabled={connecting}
          className="px-6 py-2 bg-[var(--accent)] text-white rounded-lg text-sm hover:bg-[var(--accent-hover)] disabled:opacity-50"
        >
          {connecting ? "连接中..." : "连接桌面"}
        </button>

        <div className="mt-8 rounded-lg border border-zinc-700 bg-zinc-900 p-4 text-sm text-zinc-500 max-w-md">
          <div className="mb-2 font-medium text-zinc-400">功能说明：</div>
          <ul className="list-disc pl-4 space-y-1">
            <li>noVNC 实时桌面流 (WebSocket)</li>
            <li>鼠标/键盘远程交互</li>
            <li>截屏 &amp; 录屏回放</li>
            <li>浏览器操作可视化 (CDP)</li>
            <li>分辨率 &amp; 画质自适应</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-black">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-zinc-900 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-xs text-zinc-400">已连接</span>
          </div>
          <span className="text-xs text-zinc-600">{resolution}</span>
          <span className="text-xs text-zinc-600">Q:{quality}%</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={takeScreenshot}
            className="text-xs px-2 py-1 bg-zinc-800 text-zinc-300 rounded hover:bg-zinc-700"
            title="截屏"
          >
            📸 截屏
          </button>
          <button
            onClick={() => setIsRecording(!isRecording)}
            className={`text-xs px-2 py-1 rounded ${
              isRecording
                ? "bg-red-600 text-white"
                : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
            }`}
            title={isRecording ? "停止录制" : "开始录制"}
          >
            {isRecording ? "⏹ 停止" : "⏺ 录制"}
          </button>
          <button
            onClick={() => {
              // Send Ctrl+Alt+Del
            }}
            className="text-xs px-2 py-1 bg-zinc-800 text-zinc-300 rounded hover:bg-zinc-700"
            title="Ctrl+Alt+Del"
          >
            ⌨️ CAD
          </button>
          <button
            onClick={disconnect}
            className="text-xs px-2 py-1 bg-red-900/50 text-red-400 rounded hover:bg-red-900/80"
          >
            断开
          </button>
        </div>
      </div>

      {/* Desktop canvas */}
      <div
        ref={canvasRef}
        className="flex-1 flex items-center justify-center cursor-crosshair"
        style={{ background: "#1a1a2e" }}
      >
        <div className="text-center">
          <div className="text-6xl mb-4 opacity-30">🖥️</div>
          <p className="text-zinc-600 text-sm">
            桌面流已连接 — Agent 正在沙箱中操作
          </p>
          <p className="text-zinc-700 text-xs mt-1">
            {frames.length > 0
              ? `已接收 ${frames.length} 帧`
              : "等待桌面帧..."}
          </p>
          {isRecording && (
            <div className="mt-3 flex items-center justify-center gap-2 text-red-500 text-xs">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              录制中...
            </div>
          )}
        </div>
      </div>

      {/* Keyboard shortcuts */}
      <div className="px-3 py-1 bg-zinc-900 border-t border-zinc-800 text-xs text-zinc-600 flex items-center gap-4">
        <span>F11: 全屏</span>
        <span>Ctrl+Alt+Del: 系统操作</span>
        <span>Ctrl+Shift+S: 截屏</span>
      </div>
    </div>
  );
}
