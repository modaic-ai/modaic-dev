from pydantic_settings import BaseSettings
from src.lib.logger import logger
import os
from dotenv import load_dotenv

load_dotenv(f".env")
logger.info(f"LOADING ENVIRONMENT: {os.getenv('ENVIRONMENT')}")


class Settings(BaseSettings):
    mongo_database: str
    mongo_url: str
    environment: str
    stytch_project_id: str
    stytch_secret: str
    stytch_project_domain: str
    gmail_app_password: str
    next_url: str

    class Config:
        env_file = f".env"
        extra = "ignore"


settings = Settings()
