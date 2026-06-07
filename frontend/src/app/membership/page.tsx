"use client";

import { useTranslations } from "next-intl";

export default function MembershipPage() {
  const t = useTranslations("membership");

  const members = [
    { id: "u1", name: "Admin User", email: "admin@openagent.dev", role: "admin", lastActive: "2 分钟前" },
    { id: "u2", name: "Developer", email: "dev@openagent.dev", role: "member", lastActive: "1 小时前" },
    { id: "u3", name: "Viewer", email: "viewer@openagent.dev", role: "viewer", lastActive: "3 天前" },
  ];

  const roleColors: Record<string, string> = {
    admin: "bg-red-900/30 text-red-400",
    member: "bg-blue-900/30 text-blue-400",
    viewer: "bg-gray-900/30 text-gray-400",
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">{t("description")}</p>
        </div>
        <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90">
          {t("invite")}
        </button>
      </div>

      <div className="bg-[var(--bg-secondary)] rounded-lg border border-[var(--border)] overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--border)] text-left text-sm text-[var(--text-secondary)]">
              <th className="p-4">{t("name")}</th>
              <th className="p-4">{t("email")}</th>
              <th className="p-4">{t("role")}</th>
              <th className="p-4">{t("lastActive")}</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody>
            {members.map((m) => (
              <tr key={m.id} className="border-b border-[var(--border)] last:border-0">
                <td className="p-4 font-medium">{m.name}</td>
                <td className="p-4 text-sm text-[var(--text-secondary)]">{m.email}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs ${roleColors[m.role]}`}>
                    {m.role}
                  </span>
                </td>
                <td className="p-4 text-sm text-[var(--text-secondary)]">{m.lastActive}</td>
                <td className="p-4 text-right">
                  <button className="text-sm text-[var(--accent)] hover:underline">{t("edit")}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
