"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import {
  IconChat, IconSearch, IconBook, IconShield, IconZap, IconGear,
} from "@/components/icons/Icons";
import { ReactNode } from "react";

const navItems: { key: string; href: string; icon: ReactNode }[] = [
  { key: "sessions", href: "/sessions", icon: <IconChat className="w-[18px] h-[18px]" /> },
  { key: "ask", href: "/ask", icon: <IconSearch className="w-[18px] h-[18px]" /> },
  { key: "wiki", href: "/deepwiki", icon: <IconBook className="w-[18px] h-[18px]" /> },
  { key: "review", href: "/review", icon: <IconShield className="w-[18px] h-[18px]" /> },
  { key: "automations", href: "/automations", icon: <IconZap className="w-[18px] h-[18px]" /> },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("nav");

  return (
    <aside className="w-[52px] h-screen flex flex-col bg-[var(--sidebar-bg)] border-r border-[var(--border)] items-center select-none">
      {/* Logo mark */}
      <div className="h-[42px] flex items-center justify-center w-full border-b border-[var(--border)]">
        <Link href="/" className="flex items-center justify-center w-8 h-8 rounded-md bg-[var(--accent)] hover:bg-[var(--accent-hover)] transition-colors">
          <span className="text-[11px] font-bold text-white tracking-tight">OA</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 flex flex-col items-center pt-3 gap-1 w-full">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href || pathname?.startsWith(item.href + "/");

          return (
            <Link
              key={item.key}
              href={item.href}
              title={t(item.key)}
              className={cn(
                "relative flex items-center justify-center w-9 h-9 rounded-md transition-all duration-150",
                isActive
                  ? "bg-[var(--accent-dim)] text-[var(--accent)]"
                  : "text-[var(--sidebar-text)] hover:text-[var(--sidebar-active)] hover:bg-white/[0.04]"
              )}
            >
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[2px] h-4 bg-[var(--accent)] rounded-r" />
              )}
              {item.icon}
            </Link>
          );
        })}
      </nav>

      {/* Bottom settings */}
      <div className="pb-3 flex flex-col items-center gap-1">
        <Link
          href="/settings"
          title={t("settings")}
          className={cn(
            "flex items-center justify-center w-9 h-9 rounded-md transition-all duration-150",
            pathname?.startsWith("/settings")
              ? "bg-[var(--accent-dim)] text-[var(--accent)]"
              : "text-[var(--sidebar-text)] hover:text-[var(--sidebar-active)] hover:bg-white/[0.04]"
          )}
        >
          <IconGear className="w-[18px] h-[18px]" />
        </Link>
        <div className="w-[6px] h-[6px] rounded-full bg-[var(--success)]" title="Agent Ready" />
      </div>
    </aside>
  );
}
