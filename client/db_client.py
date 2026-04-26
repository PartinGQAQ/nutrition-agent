from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()

class DBClient:
    def __init__(self):
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = os.getenv("MYSQL_PORT", "3306")
        self.database = os.getenv("MYSQL_DATABASE")

        # engine只创建一次
        self.engine = create_async_engine(
            self._get_url(),
            echo=False,          # 开发时打印SQL，生产改False
            pool_pre_ping=True, # 自动检测断连
        )

        # session工厂也只创建一次
        self._session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def _get_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    async def init_db(self):
        """建表，启动时调用一次"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            

    @asynccontextmanager
    async def session_scope(self):
        """脚本、任务等非 Depends 场景：async with db_client.session_scope() as session:"""
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """FastAPI Depends 用这个"""
        async with self.session_scope() as session:
            yield session






db_client = DBClient()