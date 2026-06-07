"use client";

import { useTranslations } from "next-intl";

export default function BillingPage() {
  const t = useTranslations("billing");

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{t("title")}</h1>

      {/* 当前用量 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-[var(--bg-secondary)] rounded-lg p-5 border border-[var(--border)]">
          <div className="text-sm text-[var(--text-secondary)] mb-1">{t("currentPlan")}</div>
          <div className="text-2xl font-bold">Pro</div>
          <div className="text-sm text-[var(--accent)] mt-1">$49/月</div>
        </div>
        <div className="bg-[var(--bg-secondary)] rounded-lg p-5 border border-[var(--border)]">
          <div className="text-sm text-[var(--text-secondary)] mb-1">{t("acuUsed")}</div>
          <div className="text-2xl font-bold">2,450</div>
          <div className="flex items-center gap-2 mt-2">
            <div className="flex-1 h-2 bg-[var(--bg-primary)] rounded-full overflow-hidden">
              <div className="h-full bg-[var(--accent)] rounded-full" style={{ width: "49%" }} />
            </div>
            <span className="text-xs text-[var(--text-secondary)]">49%</span>
          </div>
        </div>
        <div className="bg-[var(--bg-secondary)] rounded-lg p-5 border border-[var(--border)]">
          <div className="text-sm text-[var(--text-secondary)] mb-1">{t("billingCycle")}</div>
          <div className="text-2xl font-bold">2026-06</div>
          <div className="text-sm text-[var(--text-secondary)] mt-1">{t("renewsOn")} 2026-07-01</div>
        </div>
      </div>

      {/* 价格档位 */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)] mb-6">
        <h2 className="text-lg font-semibold mb-4">{t("pricing")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {[
            { tier: "XS", sessions: "< 10 min", acu: "1 ACU", price: "$0.10" },
            { tier: "S", sessions: "10-30 min", acu: "5 ACU", price: "$0.50" },
            { tier: "M", sessions: "30-120 min", acu: "25 ACU", price: "$2.50" },
            { tier: "L", sessions: "2-8 hrs", acu: "100 ACU", price: "$10.00" },
            { tier: "XL", sessions: "> 8 hrs", acu: "500 ACU", price: "$50.00" },
          ].map((p) => (
            <div key={p.tier} className="text-center p-3 rounded-lg bg-[var(--bg-primary)]">
              <div className="text-lg font-bold text-[var(--accent)]">{p.tier}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-1">{p.sessions}</div>
              <div className="text-sm font-medium mt-2">{p.acu}</div>
              <div className="text-xs text-[var(--text-secondary)]">{p.price}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 使用历史 */}
      <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border)]">
        <h2 className="text-lg font-semibold mb-4">{t("usageHistory")}</h2>
        <div className="space-y-2">
          {[
            { date: "2026-06-06", sessions: 12, acu: 145, cost: "$14.50" },
            { date: "2026-06-05", sessions: 8, acu: 98, cost: "$9.80" },
            { date: "2026-06-04", sessions: 15, acu: 210, cost: "$21.00" },
            { date: "2026-06-03", sessions: 6, acu: 72, cost: "$7.20" },
            { date: "2026-06-02", sessions: 10, acu: 130, cost: "$13.00" },
          ].map((row) => (
            <div
              key={row.date}
              className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0 text-sm"
            >
              <span className="font-mono">{row.date}</span>
              <span className="text-[var(--text-secondary)]">{row.sessions} 会话</span>
              <span className="text-[var(--text-secondary)]">{row.acu} ACU</span>
              <span className="text-[var(--accent)]">{row.cost}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
