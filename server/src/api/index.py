from src.api.user.index import router as user_router
from src.api.repo.index import router as repo_router
from src.api.auth.index import router as auth_router

__all__ = ["user_router", "repo_router", "auth_router"]
