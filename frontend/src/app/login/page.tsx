"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

export default function LoginPage() {
  const t = useTranslations("auth");
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: 接入 authApi
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg-primary)]">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[var(--accent)]">OpenAgent</h1>
          <p className="text-[var(--text-secondary)] mt-2">
            AI 驱动的全生命周期软件开发平台
          </p>
        </div>

        <div className="bg-[var(--bg-secondary)] rounded-lg border border-[var(--border)] p-6">
          {/* Tab 切换 */}
          <div className="flex mb-6 border-b border-[var(--border)]">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 pb-2 text-sm font-medium border-b-2 transition-colors ${
                isLogin
                  ? "border-[var(--accent)] text-[var(--accent)]"
                  : "border-transparent text-[var(--text-secondary)]"
              }`}
            >
              {t("login")}
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 pb-2 text-sm font-medium border-b-2 transition-colors ${
                !isLogin
                  ? "border-[var(--accent)] text-[var(--accent)]"
                  : "border-transparent text-[var(--text-secondary)]"
              }`}
            >
              {t("register")}
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-1">
                {t("username")}
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 rounded bg-[var(--bg-primary)] border border-[var(--border)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
                required
              />
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm text-[var(--text-secondary)] mb-1">
                  {t("email")}
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-[var(--bg-primary)] border border-[var(--border)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-1">
                {t("password")}
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 rounded bg-[var(--bg-primary)] border border-[var(--border)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full py-2 bg-[var(--accent)] text-white rounded font-medium hover:opacity-90 transition-opacity"
            >
              {isLogin ? t("login") : t("register")}
            </button>
          </form>

          <div className="mt-4 text-center text-xs text-[var(--text-secondary)]">
            默认账号: admin / admin123
          </div>
        </div>
      </div>
    </div>
  );
}
