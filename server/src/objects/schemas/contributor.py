from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import Optional
from enum import Enum
from src.utils.date import now


class AccessLevelEnum(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ContributorSchema(BaseModel):
    """Full contributor schema with all fields."""

    contributorId: str = Field(..., min_length=1, max_length=100)
    userId: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    agentId: str = Field(..., min_length=1, max_length=100)
    accessLevel: AccessLevelEnum = AccessLevelEnum.READ
    invitedAt: str
    acceptedAt: Optional[str] = None
    pending: bool = True
    invitedBy: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PublicContributorSchema(BaseModel):
    """Public contributor schema - what others can see."""

    contributorId: str
    username: str
    agentId: str
    accessLevel: AccessLevelEnum
    invitedAt: str
    acceptedAt: Optional[str] = None
    pending: bool

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class CreateContributorRequest(BaseModel):
    """Request schema for inviting a new contributor."""

    userId: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: EmailStr
    agentId: str = Field(..., min_length=1, max_length=100)
    accessLevel: AccessLevelEnum = AccessLevelEnum.READ

    # Auto-generated fields
    invitedAt: str = Field(default_factory=lambda: now())
    pending: bool = True

    @validator("username")
    def validate_username(cls, v: str):
        if v and not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, hyphens, and underscores"
            )
        return v.lower() if v else v

    # Must provide either userId or username
    @validator("username")
    def validate_user_identification(cls, v, values: dict):
        user_id = values.get("userId")
        if not user_id and not v:
            raise ValueError("Either userId or username must be provided")
        return v


class UpdateContributorRequest(BaseModel):
    """Request schema for updating contributor information."""

    accessLevel: Optional[AccessLevelEnum] = None

    model_config = ConfigDict(exclude_unset=True)


class AcceptInvitationRequest(BaseModel):
    """Request schema for accepting contributor invitation."""

    contributorId: str = Field(..., min_length=1, max_length=100)
    acceptedAt: str = Field(default_factory=lambda: now())


class RemoveContributorRequest(BaseModel):
    """Request schema for removing a contributor."""

    contributorId: str = Field(..., min_length=1, max_length=100)


class GetContributorRequest(BaseModel):
    """Request schema for getting contributor information."""

    contributorId: str = Field(..., min_length=1, max_length=100)
