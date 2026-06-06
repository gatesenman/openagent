"""Git 集成服务 / Git integration service.

在沙箱虚拟环境中执行 Git 操作。
支持: clone/commit/push/diff/log/branch/status/PR。
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.sandbox.base import BaseSandbox

logger = logging.getLogger(__name__)


@dataclass
class GitDiffEntry:
    """Git diff 条目."""
    path: str
    status: str  # added / modified / deleted / renamed
    additions: int = 0
    deletions: int = 0
    hunks: list[dict] = field(default_factory=list)


@dataclass
class GitLogEntry:
    """Git log 条目."""
    sha: str
    short_sha: str
    message: str
    author: str
    date: str
    files_changed: int = 0


@dataclass
class GitStatus:
    """Git status."""
    branch: str
    clean: bool
    staged: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)
    ahead: int = 0
    behind: int = 0


class GitService:
    """Git 操作服务.

    所有操作通过沙箱执行，确保隔离性。
    """

    async def clone(
        self,
        sandbox: BaseSandbox,
        repo_url: str,
        target_dir: str = "workspace",
        branch: str | None = None,
        depth: int | None = None,
    ) -> dict:
        """克隆仓库到沙箱工作区."""
        cmd = f"git clone"
        if branch:
            cmd += f" -b {branch}"
        if depth:
            cmd += f" --depth {depth}"
        cmd += f" {repo_url} {target_dir}"

        result = await sandbox.exec(cmd)
        logger.info("Git clone: %s -> %s (exit=%d)", repo_url, target_dir, result.exit_code)
        return {
            "success": result.exit_code == 0,
            "output": result.stdout,
            "error": result.stderr,
            "repo_url": repo_url,
            "target_dir": target_dir,
        }

    async def status(self, sandbox: BaseSandbox, repo_dir: str = "workspace") -> GitStatus:
        """获取 Git 状态."""
        branch_result = await sandbox.exec(
            f"cd {repo_dir} && git branch --show-current"
        )
        status_result = await sandbox.exec(
            f"cd {repo_dir} && git status --porcelain"
        )

        staged, modified, untracked = [], [], []
        for line in status_result.stdout.strip().split("\n"):
            if not line:
                continue
            idx, wt = line[0], line[1]
            filepath = line[3:].strip()
            if idx != " " and idx != "?":
                staged.append(filepath)
            if wt == "M":
                modified.append(filepath)
            if idx == "?":
                untracked.append(filepath)

        return GitStatus(
            branch=branch_result.stdout.strip(),
            clean=len(staged) == 0 and len(modified) == 0 and len(untracked) == 0,
            staged=staged,
            modified=modified,
            untracked=untracked,
        )

    async def diff(
        self,
        sandbox: BaseSandbox,
        repo_dir: str = "workspace",
        staged: bool = False,
        ref: str | None = None,
    ) -> list[GitDiffEntry]:
        """获取 Git diff."""
        cmd = f"cd {repo_dir} && git diff --numstat"
        if staged:
            cmd += " --staged"
        if ref:
            cmd += f" {ref}"

        result = await sandbox.exec(cmd)
        entries = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                add = int(parts[0]) if parts[0] != "-" else 0
                delete = int(parts[1]) if parts[1] != "-" else 0
                path = parts[2]
                status = "modified"
                entries.append(GitDiffEntry(
                    path=path, status=status,
                    additions=add, deletions=delete,
                ))
        return entries

    async def commit(
        self,
        sandbox: BaseSandbox,
        message: str,
        repo_dir: str = "workspace",
        add_all: bool = True,
    ) -> dict:
        """创建 Git commit."""
        if add_all:
            await sandbox.exec(f"cd {repo_dir} && git add -A")

        result = await sandbox.exec(
            f'cd {repo_dir} && git commit -m "{message}"'
        )
        logger.info("Git commit: %s (exit=%d)", message[:50], result.exit_code)
        return {
            "success": result.exit_code == 0,
            "output": result.stdout,
            "error": result.stderr,
        }

    async def push(
        self,
        sandbox: BaseSandbox,
        repo_dir: str = "workspace",
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict:
        """推送到远程."""
        cmd = f"cd {repo_dir} && git push {remote}"
        if branch:
            cmd += f" {branch}"
        result = await sandbox.exec(cmd)
        return {
            "success": result.exit_code == 0,
            "output": result.stdout,
            "error": result.stderr,
        }

    async def log(
        self,
        sandbox: BaseSandbox,
        repo_dir: str = "workspace",
        limit: int = 20,
    ) -> list[GitLogEntry]:
        """获取 Git log."""
        fmt = "%H|%h|%s|%an|%ai"
        result = await sandbox.exec(
            f'cd {repo_dir} && git log --format="{fmt}" -n {limit}'
        )
        entries = []
        for line in result.stdout.strip().split("\n"):
            if not line or "|" not in line:
                continue
            parts = line.split("|", 4)
            if len(parts) >= 5:
                entries.append(GitLogEntry(
                    sha=parts[0], short_sha=parts[1],
                    message=parts[2], author=parts[3], date=parts[4],
                ))
        return entries

    async def branch(
        self,
        sandbox: BaseSandbox,
        name: str,
        repo_dir: str = "workspace",
        checkout: bool = True,
    ) -> dict:
        """创建并切换分支."""
        flag = "-b" if checkout else ""
        result = await sandbox.exec(
            f"cd {repo_dir} && git checkout {flag} {name}"
        )
        return {
            "success": result.exit_code == 0,
            "branch": name,
            "output": result.stdout,
        }

    async def create_pr(
        self,
        sandbox: BaseSandbox,
        title: str,
        body: str,
        base: str = "main",
        head: str | None = None,
        repo_dir: str = "workspace",
    ) -> dict:
        """创建 Pull Request (通过 GitHub CLI 或 API)."""
        if not head:
            br = await sandbox.exec(f"cd {repo_dir} && git branch --show-current")
            head = br.stdout.strip()

        result = await sandbox.exec(
            f'cd {repo_dir} && gh pr create --title "{title}" --body "{body}" --base {base} --head {head}'
        )
        return {
            "success": result.exit_code == 0,
            "output": result.stdout,
            "error": result.stderr,
        }


git_service = GitService()
