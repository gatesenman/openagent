"use client";

import { useTranslations } from "next-intl";

export default function SnapshotsPage() {
  const t = useTranslations("snapshots");

  const snapshots = [
    {
      id: "snap-001",
      name: "python-fullstack-v2",
      blueprint: "Python + Node.js 全栈",
      status: "ready",
      size: "2.4 GB",
      created: "2026-06-05 14:30",
    },
    {
      id: "snap-002",
      name: "java-spring-v1",
      blueprint: "Java Spring Boot",
      status: "building",
      size: "-",
      created: "2026-06-06 10:15",
    },
    {
      id: "snap-003",
      name: "go-microservice-v1",
      blueprint: "Go + gRPC",
      status: "ready",
      size: "1.8 GB",
      created: "2026-06-04 09:00",
    },
  ];

  const statusConfig: Record<string, { color: string; label: string }> = {
    ready: { color: "bg-green-900/30 text-green-400", label: t("ready") },
    building: { color: "bg-yellow-900/30 text-yellow-400", label: t("building") },
    failed: { color: "bg-red-900/30 text-red-400", label: t("failed") },
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90">
          {t("build")}
        </button>
      </div>

      <div className="space-y-4">
        {snapshots.map((snap) => {
          const sc = statusConfig[snap.status];
          return (
            <div
              key={snap.id}
              className="bg-[var(--bg-secondary)] rounded-lg p-5 border border-[var(--border)]"
            >
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h3 className="font-semibold">{snap.name}</h3>
                  <span className="text-xs text-[var(--text-secondary)]">{snap.blueprint}</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${sc.color}`}>{sc.label}</span>
              </div>
              <div className="flex items-center gap-6 text-sm text-[var(--text-secondary)]">
                <span>💾 {snap.size}</span>
                <span>🕐 {snap.created}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
