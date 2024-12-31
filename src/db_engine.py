from sqlalchemy.ext.asyncio import create_async_engine

from settings import DbSettings

DATABASE_URL = (
    f"postgresql+asyncpg://{DbSettings.DB_USER}:{DbSettings.DB_PASSWORD}@{DbSettings.DB_HOST}:"
    f"{DbSettings.DB_PORT}/{DbSettings.DB_NAME}"
)

engine = create_async_engine(DATABASE_URL)
