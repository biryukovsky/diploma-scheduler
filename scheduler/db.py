from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        db_name: str
    ) -> None:
        sync_dsn = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        async_dsn = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
        self._engine = create_async_engine(async_dsn, echo=True)
        self._sync_engine = create_engine(sync_dsn)
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=AsyncSession,
        )

    @property
    def sync_engine(self):
        return self._sync_engine

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            await self._engine.dispose()
