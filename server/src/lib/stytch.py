from src.core.config import settings
from src.lib.logger import logger
from stytch import Client
from stytch.core.response_base import StytchError
from stytch.consumer.models.users import User as StytchUser

client = Client(
    project_id=settings.stytch_project_id,
    secret=settings.stytch_secret,
    environment="test" if settings.environment == "dev" else "live",
)
logger.info(f"STYTCH CLIENT INITIALIZED")
