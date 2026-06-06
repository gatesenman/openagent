"""Alembic 环境配置."""

import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# 确保 backend 目录在 path 中
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base
from app.models import session, user, audit_log, knowledge, tool  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline():
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
