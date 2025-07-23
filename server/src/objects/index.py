from src.objects.schemas.user import *
from src.objects.schemas.contributor import *
from src.objects.schemas.agent import *
from src.objects.models.user import *
from src.objects.models.contributor import *
from src.objects.models.agent import *

user_schemas = [
    "UserSchema",
    "CreateUserRequest",
    "UpdateUserRequest",
    "DeleteUserRequest",
    "GetUserRequest",
    "PublicUserSchema",
]

user_models = ["User"]

contributor_schemas = [
    "ContributorSchema",
]

contributor_models = ["Contributor"]

agent_schemas = [
    "AgentSchema",
    "CreateAgentRequest",
    "UpdateAgentRequest",
    "PublicAgentSchema",
    "AgentResponse",
    "DeleteAgentRequest",
    "GetAgentRequest",
    "StarRequest",
    "StarSchema",
    "ForkRequest",
    "ForkSchema",
    "ImageKeySchema",
    "AgentTagSchema",
]

agent_models = ["Agent", "Star", "Fork", "ImageKey", "AgentTag"]

__all__ = (
    user_schemas
    + contributor_schemas
    + agent_schemas
    + user_models
    + contributor_models
    + agent_models
)
