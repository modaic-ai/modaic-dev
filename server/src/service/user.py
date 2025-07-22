from src.objects.index import UserSchema, CreateUserRequest
from src.lib.gittea import gitea_client
from src.lib.logger import logger
from src.utils.date import now
import secrets
from typing import Union


class UserService:
    def __init__(self):
        pass

    def _generate_api_key(self) -> str:
        """Generate secure API key for SDK access"""
        return f"modaic_{secrets.token_urlsafe(32)}"

    def _encrypt_token(self, token: str) -> str:
        """Encrypt Gitea token for storage - placeholder implementation"""
        # TODO: Implement proper encryption using your preferred method
        # For now, just storing as-is (not secure for production)
        return token


user_service = UserService()
