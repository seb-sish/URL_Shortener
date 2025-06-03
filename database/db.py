from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
import contextlib
from typing import Any, AsyncIterator

import sys, os
sys.path.append(os.path.join(sys.path[0], '..'))

from utils import config, hash_password

class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine, expire_on_commit=False)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.URL_Postgres, {"echo": config.DEBUG_SQL})


async def get_session():
    async with sessionmanager.session() as session:
        yield session

async def test_connection():
    from database import models
    async for session in get_session():
        result = await session.execute(select(models.User.username).limit(1))
        print(result.scalar())
        print("Connection successful!")

        from database.models import User, Link
        session.add(User(username="sebsish", email="se6sish@gmail.com", password=hash_password("43811090")))
        await session.commit()
        session.add(Link(original_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUIcmlja3JvbGw%3D", link="RICKROLL", owner_id=1,))
        await session.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection())