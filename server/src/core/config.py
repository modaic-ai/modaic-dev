from pydantic_settings import BaseSettings
from src.lib.logger import logger
import os
from dotenv import load_dotenv

load_dotenv(f".env")
logger.info(f"LOADING ENVIRONMENT: {os.getenv('ENVIRONMENT')}")


class Settings(BaseSettings):
    environment: str
    stytch_project_id: str
    stytch_secret: str
    stytch_project_domain: str
    gmail_app_password: str
    next_url: str
    s3_bucket_name: str
    cloudfront_domain: str
    gittea_url: str
    gittea_admin_token: str
    gittea_webhook_secret: str
    postgres_database: str
    postgres_connection_url: str

    class Config:
        env_file = f".env"
        extra = "ignore"


settings = Settings()
