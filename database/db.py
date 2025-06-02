from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
import contextlib
from typing import Any, AsyncIterator

import sys
import os
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
    async with get_session() as session:
        result = await session.execute(text("SELECT * FROM users LIMIT 1"))
        print(result.scalar())
        print("Connection successful!")

        from database.models import User, Link
        session.add(User(username="test_user", email="test_user@example.com", password=hash_password("securepassword")))
        session.add(Link(original_link="https://google.com", link="EXMPL", owner_id=1,))
        await session.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection())