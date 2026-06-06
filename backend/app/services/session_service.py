"""会话服务 / Session service.

管理 Agent 会话的完整生命周期。
每个会话绑定一个沙箱虚拟环境。
"""

import logging
import uuid
from datetime import datetime
from typing import Any, AsyncIterator

from sqlalchemy.orm import Session as DBSession

from app.agent.react_engine import AgentEvent, ReactEngine
from app.models.session import Event, Message, Session
from app.sandbox.base import BaseSandbox
from app.sandbox.manager import sandbox_manager
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class SessionService:
    """会话服务.

    负责:
    1. 会话 CRUD
    2. 关联沙箱虚拟环境
    3. 触发 Agent 执行
    4. 管理消息和事件
    """

    async def create_session(
        self,
        db: DBSession,
        title: str = "新会话",
        mode: str = "cloud",
        model: str = "gpt-4o",
        platform: str = "linux",
        language: str = "zh",
        prompt: str = "",
    ) -> Session:
        """创建新会话 + 关联沙箱."""
        session_id = str(uuid.uuid4())

        session = Session(
            id=session_id,
            title=title,
            status="created",
            mode=mode,
            model=model,
            platform=platform,
            language=language,
        )
        db.add(session)

        # 创建沙箱虚拟环境
        try:
            sandbox = await sandbox_manager.create_sandbox(
                session_id=session_id,
                mode=mode,
                platform=platform,
            )
            session.status = "running"
            logger.info("会话已创建: %s, 沙箱类型: %s", session_id, type(sandbox).__name__)
        except Exception as e:
            logger.error("沙箱创建失败: %s", e)
            session.status = "failed"

        # 添加初始消息
        if prompt:
            msg = Message(
                session_id=session_id,
                role="user",
                content=prompt,
            )
            db.add(msg)

        db.commit()
        db.refresh(session)
        return session

    def get_session(self, db: DBSession, session_id: str) -> Session | None:
        """获取会话详情."""
        return db.query(Session).filter(Session.id == session_id).first()

    def list_sessions(
        self, db: DBSession, skip: int = 0, limit: int = 20, status: str | None = None
    ) -> tuple[list[Session], int]:
        """获取会话列表."""
        query = db.query(Session)
        if status:
            query = query.filter(Session.status == status)
        total = query.count()
        sessions = query.order_by(Session.created_at.desc()).offset(skip).limit(limit).all()
        return sessions, total

    def update_session(
        self, db: DBSession, session_id: str, **kwargs: Any
    ) -> Session | None:
        """更新会话."""
        session = self.get_session(db, session_id)
        if not session:
            return None
        for key, value in kwargs.items():
            if hasattr(session, key) and value is not None:
                setattr(session, key, value)
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    async def pause_session(self, db: DBSession, session_id: str) -> Session | None:
        """暂停会话 — 保存状态快照，释放沙箱资源."""
        session = self.get_session(db, session_id)
        if not session or session.status not in ("running", "idle"):
            return None
        session.status = "paused"
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        logger.info("会话已暂停: %s", session_id)
        return session

    async def resume_session(self, db: DBSession, session_id: str) -> Session | None:
        """恢复会话 — 从快照恢复沙箱."""
        session = self.get_session(db, session_id)
        if not session or session.status != "paused":
            return None
        # 重新创建沙箱
        try:
            await sandbox_manager.create_sandbox(
                session_id=session_id,
                mode=session.mode,
                platform=session.platform,
            )
            session.status = "running"
        except Exception as e:
            logger.error("恢复沙箱失败: %s", e)
            session.status = "failed"
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    async def handoff_session(
        self, db: DBSession, session_id: str, target_mode: str
    ) -> Session | None:
        """交接会话 — localhost <-> cloud 模式切换.

        例如: 本地开发完成后交给云端继续 CI/CD
        """
        session = self.get_session(db, session_id)
        if not session:
            return None
        old_mode = session.mode
        session.mode = target_mode
        session.status = "handoff"
        session.updated_at = datetime.utcnow()
        db.commit()
        # 销毁旧沙箱，创建新沙箱
        await sandbox_manager.destroy_sandbox(session_id)
        try:
            await sandbox_manager.create_sandbox(
                session_id=session_id,
                mode=target_mode,
                platform=session.platform,
            )
            session.status = "running"
        except Exception as e:
            logger.error("交接沙箱失败: %s", e)
            session.status = "failed"
        db.commit()
        db.refresh(session)
        logger.info("会话已交接: %s -> %s (%s)", session_id, target_mode, old_mode)
        return session

    async def fork_session(
        self, db: DBSession, session_id: str
    ) -> Session | None:
        """分叉会话 — 从当前状态创建新会话副本."""
        source = self.get_session(db, session_id)
        if not source:
            return None
        forked = await self.create_session(
            db=db,
            title=f"{source.title} (fork)",
            mode=source.mode,
            model=source.model,
            platform=source.platform,
            language=source.language,
        )
        logger.info("会话已分叉: %s -> %s", session_id, forked.id)
        return forked

    async def delete_session(self, db: DBSession, session_id: str) -> bool:
        """删除会话 + 销毁沙箱."""
        session = self.get_session(db, session_id)
        if not session:
            return False

        # 销毁沙箱
        await sandbox_manager.destroy_sandbox(session_id)

        db.delete(session)
        db.commit()
        return True

    async def send_message(
        self, db: DBSession, session_id: str, content: str
    ) -> AsyncIterator[AgentEvent]:
        """发送消息并触发 Agent 执行.

        这是核心流程：
        1. 保存用户消息
        2. 获取沙箱实例
        3. 构建上下文
        4. 启动 ReAct 循环
        5. 流式返回 AG-UI 事件
        """
        session = self.get_session(db, session_id)
        if not session:
            yield AgentEvent("RUN_ERROR", error="会话不存在")
            return

        # 保存用户消息
        user_msg = Message(
            session_id=session_id,
            role="user",
            content=content,
        )
        db.add(user_msg)
        db.commit()

        # 获取沙箱
        sandbox = await sandbox_manager.get_sandbox(session_id)
        if not sandbox:
            # 尝试重新创建沙箱
            try:
                sandbox = await sandbox_manager.create_sandbox(
                    session_id=session_id,
                    mode=session.mode,
                    platform=session.platform,
                )
            except Exception as e:
                yield AgentEvent("RUN_ERROR", error=f"沙箱不可用: {e}")
                return

        # 构建消息历史
        messages = self._build_message_history(db, session_id)

        # 获取 LLM 客户端
        llm_client = llm_service._get_client(session.model)

        # 创建 ReAct 引擎并执行
        engine = ReactEngine(
            sandbox=sandbox,
            llm_client=llm_client,
            model=session.model,
            language=session.language,
        )

        # 执行 ReAct 循环，流式返回事件
        async for event in engine.run(messages, session_id=session_id):
            # 保存事件到数据库
            self._save_event(db, session_id, event)

            # 保存 Agent 回复消息
            if event.type == "TEXT_MESSAGE_END":
                content_parts = []
                # 从事件数据中收集内容（简化处理）
                if "content" in event.data:
                    content_parts.append(event.data["content"])

            yield event

        # 更新会话状态
        session.updated_at = datetime.utcnow()
        db.commit()

    def get_messages(self, db: DBSession, session_id: str) -> list[Message]:
        """获取消息历史."""
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at)
            .all()
        )

    def get_events(self, db: DBSession, session_id: str) -> list[Event]:
        """获取事件历史（Worklog）."""
        return (
            db.query(Event)
            .filter(Event.session_id == session_id)
            .order_by(Event.created_at)
            .all()
        )

    def _build_message_history(
        self, db: DBSession, session_id: str
    ) -> list[dict[str, Any]]:
        """构建消息历史."""
        messages = self.get_messages(db, session_id)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
                **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {}),
            }
            for msg in messages
        ]

    def _save_event(self, db: DBSession, session_id: str, event: AgentEvent) -> None:
        """保存 Agent 事件到数据库."""
        ev = Event(
            session_id=session_id,
            event_type=event.type,
            title=event.type,
            content=event.data.get("delta") or event.data.get("content") or event.data.get("output"),
            metadata_=event.data,
            duration_ms=event.data.get("duration_ms"),
        )
        db.add(ev)
        # 批量提交，不是每个事件都 commit
        try:
            db.flush()
        except Exception:
            pass


# 全局单例
session_service = SessionService()
