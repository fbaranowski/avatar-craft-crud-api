from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database.db_engine import engine


def async_session_generator():
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_db_session():
    try:
        async_session = async_session_generator()
        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
