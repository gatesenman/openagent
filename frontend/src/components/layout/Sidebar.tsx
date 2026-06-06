"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

const navItems = [
  { key: "sessions", href: "/sessions", icon: "💬" },
  { key: "batch", href: "/batch", icon: "🔀" },
  { key: "deepwiki", href: "/deepwiki", icon: "📚" },
  { key: "codemaps", href: "/codemaps", icon: "🗺️" },
  { key: "knowledge", href: "/knowledge", icon: "🧠" },
  { key: "playbooks", href: "/playbooks", icon: "📋" },
  { key: "repos", href: "/repos", icon: "📁" },
  { key: "automations", href: "/automations", icon: "⚡" },
  { key: "mcp", href: "/mcp", icon: "🔌" },
  { key: "secrets", href: "/secrets", icon: "🔑" },
  { key: "blueprints", href: "/blueprints", icon: "🏗️" },
  { key: "apikeys", href: "/api-keys", icon: "🔐" },
  { key: "membership", href: "/membership", icon: "👥" },
  { key: "billing", href: "/billing", icon: "💰" },
  { key: "analytics", href: "/analytics", icon: "📊" },
  { key: "settings", href: "/settings", icon: "⚙️" },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("nav");

  return (
    <aside className="w-56 h-screen flex flex-col bg-[var(--sidebar-bg)] border-r border-[var(--border)]">
      {/* Logo */}
      <div className="p-4 border-b border-[var(--border)]">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            OpenAgent
          </span>
        </Link>
      </div>

      {/* 新建会话按钮 */}
      <div className="p-3">
        <Link
          href="/sessions?new=true"
          className="flex items-center justify-center gap-2 w-full px-3 py-2 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-sm font-medium transition-colors"
        >
          <span>+</span>
          <span>{t("newSession")}</span>
        </Link>
      </div>

      {/* 导航菜单 */}
      <nav className="flex-1 px-2 py-1 space-y-1">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href || pathname?.startsWith(item.href + "/");

          return (
            <Link
              key={item.key}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-[var(--accent)]/10 text-[var(--accent)]"
                  : "text-[var(--sidebar-text)] hover:bg-white/5"
              )}
            >
              <span>{item.icon}</span>
              <span>{t(item.key)}</span>
            </Link>
          );
        })}
      </nav>

      {/* 底部状态 */}
      <div className="p-3 border-t border-[var(--border)]">
        <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
          <span className="w-2 h-2 rounded-full bg-[var(--success)]" />
          <span>Agent Ready</span>
        </div>
      </div>
    </aside>
  );
}
