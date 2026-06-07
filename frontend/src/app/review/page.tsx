"use client";

export default function ReviewPage() {
  const reviews = [
    { id: "PR-42", title: "Add user authentication", repo: "openagent/backend", status: "pending", risk: "medium", files: 8 },
    { id: "PR-41", title: "Fix database migration", repo: "openagent/backend", status: "approved", risk: "low", files: 3 },
    { id: "PR-40", title: "Update dependencies", repo: "openagent/frontend", status: "changes_requested", risk: "high", files: 2 },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-1">Review</h1>
      <p className="text-sm text-[var(--text-secondary)] mb-6">
        Agent-powered PR review with security analysis and code quality checks.
      </p>

      <div className="space-y-3">
        {reviews.map((pr) => (
          <div
            key={pr.id}
            className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border)] flex items-center justify-between"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium">{pr.title}</span>
                <span className="text-xs text-[var(--text-secondary)] font-mono">{pr.id}</span>
              </div>
              <div className="text-xs text-[var(--text-secondary)]">
                {pr.repo} | {pr.files} files
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs px-2 py-0.5 rounded ${
                pr.risk === "low" ? "bg-green-500/20 text-green-400" :
                pr.risk === "medium" ? "bg-yellow-500/20 text-yellow-400" :
                "bg-red-500/20 text-red-400"
              }`}>
                {pr.risk}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded ${
                pr.status === "approved" ? "bg-green-500/20 text-green-400" :
                pr.status === "pending" ? "bg-yellow-500/20 text-yellow-400" :
                "bg-red-500/20 text-red-400"
              }`}>
                {pr.status.replace("_", " ")}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
