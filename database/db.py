import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

sys.path.append("..")  # Adjust path to import config from utils

from utils import config

engine = create_async_engine(config.URL_Postgres,
                                echo=config.DEBUG_SQL,
                                pool_size=5,
                                max_overflow=10,
                                connect_args={"check_same_thread": False}
                                )

new_async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_async_session() as session:
        yield session


if __name__ == "__main__":
    from sqlalchemy import text

    async def test_connection():
        async with new_async_session() as session:
            result = await session.execute(text("SELECT 1"))
            print(result.scalar())

    import asyncio
    asyncio.run(test_connection())