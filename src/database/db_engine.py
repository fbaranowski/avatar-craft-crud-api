from sqlalchemy.ext.asyncio import create_async_engine

from database.settings import DbSettings

DATABASE_URL = (
    f"postgresql+asyncpg://{DbSettings.DB_USER}:{DbSettings.DB_PASSWORD}@crud-db:"
    f"5432/{DbSettings.DB_NAME}"
)

engine = create_async_engine(DATABASE_URL)
