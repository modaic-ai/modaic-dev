from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from src.utils.date import now

class UserSchema(BaseModel):
    userId: str
    username: str
    email: str
    created: str = Field(default_factory=lambda: now())
    updated: str = Field(default_factory=lambda: now())
    imageKey: Optional[str] = None
    fullName: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    giteaUserId: Optional[int] = None
    giteaTokenEncrypted: Optional[str] = None
    apiKey: Optional[str] = None

    class Config:
        orm_mode = True


class CreateUserRequest(BaseModel):
    userId: str
    username: str
    email: str
    imageKey: Optional[str] = None
    fullName: Optional[str] = None
    profilePictureUrl: Optional[str] = None


class UpdateUserRequest(BaseModel):
    userId: str
    username: Optional[str] = None
    email: Optional[str] = None
    imageKey: Optional[str] = None
    fullName: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    updated: str = Field(default_factory=lambda: now())


class DeleteUserRequest(BaseModel):
    userId: str


class PublicUserSchema(BaseModel):
    userId: str
    username: str
    email: str
    created: str
    updated: str
    imageKey: Optional[str] = None
    fullName: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    giteaUserId: Optional[int] = None

    model_config = ConfigDict(extra="ignore")


class GetUserRequest(BaseModel):
    userId: str
    authorized: bool = False
