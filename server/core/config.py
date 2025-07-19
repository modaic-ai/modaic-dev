from pydantic_settings import BaseSettings
from server.lib.index import logger
import os
from dotenv import load_dotenv

load_dotenv(f".env")
logger.info(f"LOADING ENVIRONMENT: {os.getenv('ENVIRONMENT')}")


class Settings(BaseSettings):
    mongo_database: str
    mongo_url: str
    environment: str

    class Config:
        env_file = f".env"
        extra = "ignore"


settings = Settings()
