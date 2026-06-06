"""知识库数据模型 / Knowledge data models."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON

from app.core.database import Base


class Knowledge(Base):
    """知识条目."""

    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    scope = Column(String(50), default="session")  # session / repo / global
    repo_url = Column(String(500), nullable=True)
    folder = Column(String(255), nullable=True)
    pinned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SymbolIndex(Base):
    """DeepWiki 符号索引."""

    __tablename__ = "symbol_index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_url = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    symbol_name = Column(String(200), nullable=False)
    symbol_kind = Column(String(50), nullable=False)
    language = Column(String(50), nullable=True)
    signature = Column(Text, nullable=True)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    docstring = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)
    documentation = Column(JSON, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)


class ModuleMap(Base):
    """CodeMap 模块映射."""

    __tablename__ = "module_map"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_url = Column(String(500), nullable=False)
    module_path = Column(String(500), nullable=False)
    module_name = Column(String(200), nullable=False)
    language = Column(String(50), nullable=True)
    exports = Column(JSON, nullable=True)
    imports = Column(JSON, nullable=True)
    size_lines = Column(Integer, nullable=True)
    complexity = Column(Integer, nullable=True)
    dependencies = Column(JSON, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)
