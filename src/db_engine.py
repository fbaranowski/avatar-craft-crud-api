import os
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

find_dotenv()

load_dotenv()

# DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/avatar_craft_crud_db"
DATABASE_URL = (f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
                f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

engine = create_async_engine(DATABASE_URL)
