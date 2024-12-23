from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from db_engine import engine


# session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
def async_session_generator():
    return sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


@asynccontextmanager
async def get_db_session():
    try:
        async_session = async_session_generator()
        print('try start')
        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        print('finally done')
        await session.close()
