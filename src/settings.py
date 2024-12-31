import os

from dotenv import find_dotenv, load_dotenv

find_dotenv()

load_dotenv()


class DbSettings:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")


class RunwareSettings:
    RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")