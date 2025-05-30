from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from utils import config

engine = create_async_engine(config.db.URL_Postgres,
                                echo=config.db.DEBUG_SQL,
                                pool_size=5,
                                max_overflow=10,
                                connect_args={"check_same_thread": False}
                                )

new_async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_async_session() as session:
        yield session
