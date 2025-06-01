from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager

import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))

from utils import config

engine = create_async_engine(config.URL_Postgres,
                                echo=config.DEBUG_SQL,
                                pool_size=5,
                                max_overflow=10
                                )

def async_session_generator():
    return sessionmaker(
        engine, class_=AsyncSession
    )

@asynccontextmanager
async def get_session():
    try:
        async_session = async_session_generator()

        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()

if __name__ == "__main__":
    from sqlalchemy import text

    async def test_connection():
        async with get_session() as session:
            result = await session.execute(text("SELECT * FROM users LIMIT 1"))
            print(result.scalar())
            print("Connection successful!")

    import asyncio
    asyncio.run(test_connection())