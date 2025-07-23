from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum

from src.utils.date import now


class VisibilityEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class AgentSchema(BaseModel):
    agentId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=2000)
    adminId: str = Field(..., min_length=1, max_length=100)
    configYaml: str = Field(default="", max_length=50000)
    readmeContent: str = Field(default="", max_length=50000)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    lastMirrored: Optional[str] = None
    created: str = Field(default_factory=now)
    updated: str = Field(default_factory=now)
    visibility: VisibilityEnum = VisibilityEnum.PRIVATE

    # computed fields
    stars_count: int = Field(default=0, ge=0)
    forks_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=2000)
    configYaml: str = Field(default="", max_length=50000)
    readmeContent: str = Field(default="", max_length=50000)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    visibility: VisibilityEnum = VisibilityEnum.PRIVATE


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    visibility: Optional[VisibilityEnum] = None
    configYaml: Optional[str] = Field(None, max_length=50000)
    readmeContent: Optional[str] = Field(None, max_length=50000)
    tags: Optional[list[str]] = Field(None, max_items=20)
    imageKeys: Optional[list[str]] = Field(None, max_items=10)

    model_config = ConfigDict(exclude_unset=True)


class PublicAgentSchema(BaseModel):
    agentId: str
    name: str
    description: str
    visibility: VisibilityEnum
    adminId: str
    created: str
    updated: str
    stars_count: int
    forks_count: int
    forkedFrom: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AgentResponse(BaseModel):
    success: bool
    data: Optional[AgentSchema] = None
    message: Optional[str] = None


class DeleteAgentRequest(BaseModel):
    agentId: str = Field(..., min_length=1, max_length=100)


class GetAgentRequest(BaseModel):
    agentId: str = Field(..., min_length=1, max_length=100)
    authorized: bool = False


class StarRequest(BaseModel):
    agentId: str = Field(..., min_length=1, max_length=100)
    userId: str = Field(..., min_length=1, max_length=100)


class StarSchema(BaseModel):
    starId: str
    agentId: str
    userId: str
    created: str = Field(default_factory=now)

    model_config = ConfigDict(from_attributes=True)


class ForkRequest(BaseModel):
    agentId: str = Field(..., min_length=1, max_length=100)
    userId: str = Field(..., min_length=1, max_length=100)


class ForkSchema(BaseModel):
    forkId: str
    agentId: str
    userId: str
    forkedAgentId: str
    created: str = Field(default_factory=now)

    model_config = ConfigDict(from_attributes=True)


class ImageKeySchema(BaseModel):
    imageKeyId: str
    agentId: str
    imageKey: str = Field(..., min_length=1, max_length=500)
    created: str = Field(default_factory=now)

    model_config = ConfigDict(from_attributes=True)


class AgentTagSchema(BaseModel):
    tagId: str
    agentId: str
    tag: str = Field(..., min_length=1, max_length=50)
    created: str = Field(default_factory=now)

    model_config = ConfigDict(from_attributes=True)
