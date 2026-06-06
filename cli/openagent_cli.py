#!/usr/bin/env python3
"""OpenAgent CLI — 命令行工具.

支持三种模式:
- localhost: 本地 Docker 沙箱
- cascade: Windsurf 集成
- cloud: 远程云端

用法:
    openagent init          # 初始化项目
    openagent start         # 启动本地服务
    openagent session new   # 创建会话
    openagent session list  # 列出会话
    openagent session logs  # 查看会话日志
    openagent handoff       # 交接会话 (本地 ↔ 云端)
    openagent status        # 查看服务状态
    openagent config        # 查看/设置配置
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

DEFAULT_API_URL = "http://localhost:8000"
CONFIG_DIR = Path.home() / ".openagent"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """加载配置."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {
        "api_url": DEFAULT_API_URL,
        "mode": "localhost",
        "language": "zh",
        "model": "gpt-4o",
    }


def save_config(config: dict):
    """保存配置."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def api_request(method: str, path: str, data: dict | None = None) -> dict:
    """发送 API 请求."""
    config = load_config()
    url = f"{config['api_url']}{path}"
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urlopen(req, timeout=10)
        return json.loads(resp.read())
    except URLError as e:
        print(f"❌ 连接失败: {e}")
        print(f"   请确认服务是否运行: {config['api_url']}")
        sys.exit(1)


def cmd_init(args):
    """初始化项目."""
    print("🚀 OpenAgent 项目初始化")
    config = load_config()

    # 检测当前目录
    cwd = Path.cwd()
    agents_md = cwd / "AGENTS.md"

    if not agents_md.exists():
        agents_md.write_text(
            "# AGENTS.md\n\n"
            "## OpenAgent 项目配置\n\n"
            "### 环境\n- 语言: Python/TypeScript\n"
            "- 框架: FastAPI + Next.js\n\n"
            "### 规则\n- 提交前运行 lint\n- 测试覆盖率 > 80%\n"
        )
        print(f"  ✅ 创建 AGENTS.md")

    # 创建 .openagent 目录
    local_dir = cwd / ".openagent"
    local_dir.mkdir(exist_ok=True)
    (local_dir / "skills").mkdir(exist_ok=True)
    print(f"  ✅ 创建 .openagent/ 目录")

    save_config(config)
    print(f"  ✅ 配置保存到 {CONFIG_FILE}")
    print(f"\n模式: {config['mode']} | API: {config['api_url']}")
    print("运行 `openagent start` 启动服务")


def cmd_start(args):
    """启动本地服务."""
    config = load_config()
    mode = args.mode or config["mode"]

    if mode == "localhost":
        print("🐳 启动本地 Docker 沙箱模式...")
        print("   docker-compose up -d")
        os.system("docker-compose up -d 2>/dev/null || docker compose up -d 2>/dev/null")
    elif mode == "cloud":
        print("☁️  连接到云端服务...")
        print(f"   API: {config['api_url']}")
        # 检查连接
        try:
            result = api_request("GET", "/health")
            print(f"   ✅ 已连接 | 活跃沙箱: {result.get('active_sandboxes', 0)}")
        except SystemExit:
            print("   ❌ 无法连接到云端服务")
    else:
        print(f"🌊 Cascade 模式 (Windsurf 集成)")
        print("   请在 Windsurf 中配置 MCP Server")


def cmd_session_new(args):
    """创建新会话."""
    config = load_config()
    data = {
        "title": args.title or "CLI 会话",
        "mode": args.mode or config["mode"],
        "model": args.model or config["model"],
        "prompt": args.prompt or "",
    }
    result = api_request("POST", "/api/sessions/", data)
    session_id = result.get("id", "unknown")
    print(f"✅ 会话已创建: {session_id}")
    print(f"   模式: {data['mode']} | 模型: {data['model']}")
    if data["prompt"]:
        print(f"   提示: {data['prompt'][:80]}...")


def cmd_session_list(args):
    """列出会话."""
    result = api_request("GET", "/api/sessions/")
    sessions = result.get("sessions", [])
    if not sessions:
        print("暂无会话")
        return
    print(f"共 {len(sessions)} 个会话:\n")
    for s in sessions:
        status_icon = {
            "running": "🟢",
            "paused": "🟡",
            "completed": "✅",
            "failed": "🔴",
        }.get(s.get("status", ""), "⚪")
        print(f"  {status_icon} {s.get('id', '')[:8]}  {s.get('title', '')}  [{s.get('status', '')}]")


def cmd_session_logs(args):
    """查看会话日志."""
    session_id = args.session_id
    result = api_request("GET", f"/api/worklog/{session_id}")
    timeline = result.get("timeline", [])
    if not timeline:
        print("暂无日志")
        return
    for entry in timeline:
        cat = entry.get("category", "")
        title = entry.get("title", "")
        icons = {
            "think": "🧠",
            "tool_call": "🔧",
            "command": "💻",
            "code_edit": "📝",
            "git": "🔀",
            "error": "❌",
            "milestone": "🏁",
        }
        icon = icons.get(cat, "📋")
        print(f"  {icon} [{cat}] {title}")


def cmd_handoff(args):
    """交接会话."""
    session_id = args.session_id
    target = args.target
    print(f"🔄 交接会话 {session_id[:8]}... → {target}")
    result = api_request(
        "POST",
        f"/api/sessions/{session_id}/handoff",
        {"target_mode": target},
    )
    print(f"  ✅ 交接完成: {result.get('mode', target)}")


def cmd_status(args):
    """查看服务状态."""
    config = load_config()
    print(f"📊 OpenAgent 状态")
    print(f"   模式: {config['mode']}")
    print(f"   API: {config['api_url']}")
    try:
        result = api_request("GET", "/health")
        print(f"   状态: 🟢 运行中")
        print(f"   活跃沙箱: {result.get('active_sandboxes', 0)}")
    except SystemExit:
        print(f"   状态: 🔴 未连接")


def cmd_config(args):
    """查看/设置配置."""
    config = load_config()
    if args.key and args.value:
        config[args.key] = args.value
        save_config(config)
        print(f"✅ {args.key} = {args.value}")
    else:
        print("当前配置:")
        for k, v in config.items():
            print(f"  {k}: {v}")


def main():
    parser = argparse.ArgumentParser(
        prog="openagent",
        description="OpenAgent CLI — AI 驱动的全生命周期开发平台",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    subparsers.add_parser("init", help="初始化项目")

    # start
    p_start = subparsers.add_parser("start", help="启动服务")
    p_start.add_argument("--mode", choices=["localhost", "cascade", "cloud"])

    # session
    p_session = subparsers.add_parser("session", help="会话管理")
    session_sub = p_session.add_subparsers(dest="session_cmd")

    p_new = session_sub.add_parser("new", help="创建会话")
    p_new.add_argument("--title", default="")
    p_new.add_argument("--mode", default="")
    p_new.add_argument("--model", default="")
    p_new.add_argument("--prompt", default="")

    session_sub.add_parser("list", help="列出会话")

    p_logs = session_sub.add_parser("logs", help="查看日志")
    p_logs.add_argument("session_id", help="会话ID")

    # handoff
    p_handoff = subparsers.add_parser("handoff", help="交接会话")
    p_handoff.add_argument("session_id", help="会话ID")
    p_handoff.add_argument("target", choices=["localhost", "cloud"], help="目标模式")

    # status
    subparsers.add_parser("status", help="查看状态")

    # config
    p_config = subparsers.add_parser("config", help="配置管理")
    p_config.add_argument("key", nargs="?", help="配置键")
    p_config.add_argument("value", nargs="?", help="配置值")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "start": cmd_start,
        "session": lambda a: {
            "new": cmd_session_new,
            "list": cmd_session_list,
            "logs": cmd_session_logs,
        }.get(a.session_cmd, lambda _: p_session.print_help())(a),
        "handoff": cmd_handoff,
        "status": cmd_status,
        "config": cmd_config,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
