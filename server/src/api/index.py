from src.api.v1.user.index import router as user_router
from src.api.v1.auth.index import router as auth_router
from src.api.v1.contributor.index import router as contributor_router
from src.api.v1.webhook.index import router as webhook_router
from src.api.v1.agent.index import router as agent_router

__all__ = [
    "user_router",
    "auth_router",
    "contributor_router",
    "webhook_router",
    "agent_router",
]
