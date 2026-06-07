"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import {
  IconChat, IconRefresh, IconBook, IconGlobe, IconBulb, IconClipboard,
  IconFolder, IconZap, IconPuzzle, IconKey, IconServer, IconLock,
  IconUsers, IconChart, IconSave, IconCalendar, IconShield,
  IconTrend, IconRocket, IconGear, IconPackage,
} from "@/components/icons/Icons";
import { ReactNode } from "react";

const navItems: { key: string; href: string; icon: ReactNode }[] = [
  { key: "sessions", href: "/sessions", icon: <IconChat className="w-4 h-4" /> },
  { key: "batch", href: "/batch", icon: <IconRefresh className="w-4 h-4" /> },
  { key: "deepwiki", href: "/deepwiki", icon: <IconBook className="w-4 h-4" /> },
  { key: "codemaps", href: "/codemaps", icon: <IconGlobe className="w-4 h-4" /> },
  { key: "knowledge", href: "/knowledge", icon: <IconBulb className="w-4 h-4" /> },
  { key: "playbooks", href: "/playbooks", icon: <IconClipboard className="w-4 h-4" /> },
  { key: "repos", href: "/repos", icon: <IconFolder className="w-4 h-4" /> },
  { key: "automations", href: "/automations", icon: <IconZap className="w-4 h-4" /> },
  { key: "mcp", href: "/mcp", icon: <IconPuzzle className="w-4 h-4" /> },
  { key: "secrets", href: "/secrets", icon: <IconKey className="w-4 h-4" /> },
  { key: "blueprints", href: "/blueprints", icon: <IconServer className="w-4 h-4" /> },
  { key: "apikeys", href: "/api-keys", icon: <IconLock className="w-4 h-4" /> },
  { key: "membership", href: "/membership", icon: <IconUsers className="w-4 h-4" /> },
  { key: "billing", href: "/billing", icon: <IconChart className="w-4 h-4" /> },
  { key: "cicd", href: "/cicd", icon: <IconSave className="w-4 h-4" /> },
  { key: "snapshots", href: "/snapshots", icon: <IconPackage className="w-4 h-4" /> },
  { key: "schedules", href: "/schedules", icon: <IconCalendar className="w-4 h-4" /> },
  { key: "security", href: "/security", icon: <IconShield className="w-4 h-4" /> },
  { key: "analytics", href: "/analytics", icon: <IconTrend className="w-4 h-4" /> },
  { key: "onboarding", href: "/onboarding", icon: <IconRocket className="w-4 h-4" /> },
  { key: "settings", href: "/settings", icon: <IconGear className="w-4 h-4" /> },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("nav");

  return (
    <aside className="w-56 h-screen flex flex-col bg-[var(--sidebar-bg)] border-r border-[var(--border)]">
      <div className="p-4 border-b border-[var(--border)]">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            OpenAgent
          </span>
        </Link>
      </div>

      <div className="p-3">
        <Link
          href="/sessions?new=true"
          className="flex items-center justify-center gap-2 w-full px-3 py-2 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-sm font-medium transition-colors"
        >
          <span>+</span>
          <span>{t("newSession")}</span>
        </Link>
      </div>

      <nav className="flex-1 px-2 py-1 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href || pathname?.startsWith(item.href + "/");

          return (
            <Link
              key={item.key}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-1.5 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-[var(--accent)]/10 text-[var(--accent)]"
                  : "text-[var(--sidebar-text)] hover:bg-white/5"
              )}
            >
              {item.icon}
              <span>{t(item.key)}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-[var(--border)]">
        <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
          <span className="w-2 h-2 rounded-full bg-[var(--success)]" />
          <span>Agent Ready</span>
        </div>
      </div>
    </aside>
  );
}
