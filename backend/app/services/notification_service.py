"""通知集成服务 / Notification Service.

支持多渠道通知:
- In-App (WebSocket 推送)
- Slack / 飞书 / 钉钉 (Webhook)
- Email (SMTP)
- GitHub PR 评论
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    SLACK = "slack"
    FEISHU = "feishu"
    DINGTALK = "dingtalk"
    EMAIL = "email"
    GITHUB = "github"
    WEBHOOK = "webhook"


class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class Notification:
    """通知条目."""
    id: str = ""
    user_id: str = ""
    channel: NotificationChannel = NotificationChannel.IN_APP
    level: NotificationLevel = NotificationLevel.INFO
    title: str = ""
    body: str = ""
    link: str = ""
    session_id: str = ""
    read: bool = False
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class ChannelConfig:
    """通知渠道配置."""
    channel: NotificationChannel
    webhook_url: str = ""
    enabled: bool = True
    settings: dict = field(default_factory=dict)


class NotificationService:
    """多渠道通知服务."""

    def __init__(self):
        self._notifications: list[Notification] = []
        self._channels: dict[str, ChannelConfig] = {}
        self._subscribers: dict[str, list[NotificationChannel]] = {}

    def configure_channel(self, config: ChannelConfig):
        """配置通知渠道."""
        self._channels[config.channel.value] = config

    def subscribe(self, user_id: str, channels: list[NotificationChannel]):
        """订阅通知渠道."""
        self._subscribers[user_id] = channels

    async def send(
        self,
        user_id: str,
        title: str,
        body: str = "",
        level: NotificationLevel | str = NotificationLevel.INFO,
        link: str = "",
        session_id: str = "",
        channels: list[NotificationChannel] | None = None,
    ) -> list[Notification]:
        """发送通知到所有已订阅渠道."""
        if isinstance(level, str):
            level = NotificationLevel(level)
        target_channels = channels or self._subscribers.get(
            user_id, [NotificationChannel.IN_APP]
        )
        sent: list[Notification] = []

        for ch in target_channels:
            notif = Notification(
                user_id=user_id,
                channel=ch,
                level=level,
                title=title,
                body=body,
                link=link,
                session_id=session_id,
            )
            self._notifications.append(notif)

            config = self._channels.get(ch.value)
            if config and config.enabled and config.webhook_url:
                await self._dispatch(notif, config)

            sent.append(notif)

        return sent

    async def _dispatch(self, notif: Notification, config: ChannelConfig):
        """分发到外部渠道 (Phase 1: 日志记录, Phase 2: 实际HTTP调用)."""
        logger.info(
            "通知分发 → %s [%s] %s",
            config.channel.value, notif.level.value, notif.title
        )
        # Phase 2: 实际 HTTP webhook 调用
        # async with httpx.AsyncClient() as client:
        #     payload = self._format_payload(notif, config)
        #     await client.post(config.webhook_url, json=payload)

    def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[dict]:
        """获取用户通知列表."""
        results = [
            n for n in self._notifications
            if n.user_id == user_id and (not unread_only or not n.read)
        ]
        results.sort(key=lambda n: n.created_at, reverse=True)
        return [
            {
                "id": n.id,
                "channel": n.channel.value,
                "level": n.level.value,
                "title": n.title,
                "body": n.body,
                "link": n.link,
                "read": n.read,
                "created_at": n.created_at,
            }
            for n in results[:limit]
        ]

    def mark_read(self, notification_id: str) -> bool:
        """标记已读."""
        for n in self._notifications:
            if n.id == notification_id:
                n.read = True
                return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        """标记所有已读."""
        count = 0
        for n in self._notifications:
            if n.user_id == user_id and not n.read:
                n.read = True
                count += 1
        return count

    def get_channel_configs(self) -> list[dict]:
        """获取所有渠道配置."""
        return [
            {
                "channel": c.channel.value,
                "enabled": c.enabled,
                "has_webhook": bool(c.webhook_url),
            }
            for c in self._channels.values()
        ]


notification_service = NotificationService()
