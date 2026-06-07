"""Pytest fixtures / 测试配置."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# 确保 backend 在 path 中
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


@pytest.fixture
def client():
    """FastAPI 测试客户端."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """已认证的请求头."""
    resp = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
