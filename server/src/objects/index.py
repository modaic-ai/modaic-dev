from src.objects.schemas.repo import *
from src.objects.schemas.user import *
from src.objects.schemas.contributor import *
from src.objects.schemas.agent import *
from src.objects.models.repo import *
from src.objects.models.user import *
from src.objects.models.contributor import *
from src.objects.models.agent import *

repo_schemas = [
    "RepoSchema",
    "CreateRepoRequest",
    "UpdateRepoRequest",
    "DeleteRepoRequest",
    "GetRepoRequest",
    "PublicRepoSchema",
    "StarSchema",
    "ForkSchema",
    "ImageKeySchema",
    "RepoTagSchema",
]

repo_models = ["Repo", "Star", "Fork", "ImageKey", "RepoTag"]

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
]

agent_models = ["Agent"]

__all__ = repo_schemas + user_schemas + contributor_schemas + agent_schemas
