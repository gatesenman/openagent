"use client";

/**
 * 桌面面板 / Desktop panel.
 * Phase 1: 占位展示，提示 Phase 2 将支持 VNC 远程桌面。
 * Phase 2: 实际 VNC/noVNC 集成，显示沙箱内的桌面环境。
 */

export function DesktopPanel() {
  return (
    <div className="flex h-full flex-col items-center justify-center bg-zinc-950 p-8">
      <div className="mb-4 text-6xl">🖥️</div>
      <h3 className="mb-2 text-lg font-semibold text-white">
        远程桌面
      </h3>
      <p className="mb-4 max-w-md text-center text-sm text-zinc-400">
        Agent 在沙箱虚拟环境中的桌面操作将实时显示在此面板。
        支持查看浏览器测试、GUI 应用操作、截屏录制等。
      </p>
      <div className="rounded-lg border border-zinc-700 bg-zinc-900 p-4 text-sm text-zinc-500">
        <div className="mb-2 font-medium text-zinc-400">Phase 2 功能规划：</div>
        <ul className="list-disc pl-4 space-y-1">
          <li>noVNC 实时桌面流</li>
          <li>鼠标/键盘交互</li>
          <li>截屏 & 录屏回放</li>
          <li>浏览器操作可视化</li>
          <li>KVM 虚拟机桌面支持</li>
        </ul>
      </div>
      <div className="mt-6 flex items-center gap-2 text-xs text-zinc-600">
        <div className="h-2 w-2 rounded-full bg-yellow-500/50" />
        Phase 2 — 计划中
      </div>
    </div>
  );
}
