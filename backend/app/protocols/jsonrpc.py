"""JSON-RPC 2.0 基础层 / JSON-RPC 2.0 base layer.

所有协议（MCP、A2A、AG-UI）的底层通信基础。
遵循 JSON-RPC 2.0 规范: https://www.jsonrpc.org/specification
"""

import json
import uuid
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class JsonRpcErrorCode(IntEnum):
    """JSON-RPC 2.0 标准错误码."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # 自定义扩展 (-32000 ~ -32099)
    TOOL_EXECUTION_ERROR = -32001
    SANDBOX_ERROR = -32002
    LLM_ERROR = -32003
    AUTH_ERROR = -32004
    RATE_LIMIT_ERROR = -32005


@dataclass
class JsonRpcError:
    """JSON-RPC 2.0 错误对象."""

    code: int
    message: str
    data: Any = None

    def to_dict(self) -> dict:
        result = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


@dataclass
class JsonRpcRequest:
    """JSON-RPC 2.0 请求."""

    method: str
    params: dict | list | None = None
    id: str | int | None = field(default_factory=lambda: str(uuid.uuid4()))
    jsonrpc: str = "2.0"

    def to_dict(self) -> dict:
        result: dict[str, Any] = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "JsonRpcRequest":
        return cls(
            method=data["method"],
            params=data.get("params"),
            id=data.get("id"),
        )


@dataclass
class JsonRpcResponse:
    """JSON-RPC 2.0 响应."""

    id: str | int | None
    result: Any = None
    error: JsonRpcError | None = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> dict:
        resp: dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            resp["error"] = self.error.to_dict()
        else:
            resp["result"] = self.result
        return resp

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def success(cls, id: str | int | None, result: Any) -> "JsonRpcResponse":
        return cls(id=id, result=result)

    @classmethod
    def failure(
        cls, id: str | int | None, code: int, message: str, data: Any = None
    ) -> "JsonRpcResponse":
        return cls(id=id, error=JsonRpcError(code=code, message=message, data=data))


@dataclass
class JsonRpcNotification:
    """JSON-RPC 2.0 通知（无 id）."""

    method: str
    params: dict | list | None = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> dict:
        result: dict[str, Any] = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.params is not None:
            result["params"] = self.params
        return result


class JsonRpcRouter:
    """JSON-RPC 方法路由器.

    注册方法处理器，根据请求分发调用。
    """

    def __init__(self):
        self._handlers: dict[str, Any] = {}

    def method(self, name: str):
        """注册方法装饰器."""
        def decorator(func):
            self._handlers[name] = func
            return func
        return decorator

    def register(self, name: str, handler) -> None:
        """手动注册方法处理器."""
        self._handlers[name] = handler

    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        """处理 JSON-RPC 请求."""
        handler = self._handlers.get(request.method)
        if handler is None:
            return JsonRpcResponse.failure(
                request.id,
                JsonRpcErrorCode.METHOD_NOT_FOUND,
                f"方法不存在: {request.method}",
            )
        try:
            if request.params is None:
                result = await handler()
            elif isinstance(request.params, dict):
                result = await handler(**request.params)
            else:
                result = await handler(*request.params)
            return JsonRpcResponse.success(request.id, result)
        except TypeError as e:
            return JsonRpcResponse.failure(
                request.id,
                JsonRpcErrorCode.INVALID_PARAMS,
                f"参数错误: {e}",
            )
        except Exception as e:
            return JsonRpcResponse.failure(
                request.id,
                JsonRpcErrorCode.INTERNAL_ERROR,
                f"内部错误: {e}",
            )

    def list_methods(self) -> list[str]:
        """列出所有已注册的方法."""
        return list(self._handlers.keys())
