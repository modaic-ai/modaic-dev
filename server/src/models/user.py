from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from pytz import UTC
from typing import Optional
from src.db.mongo import get_collection

Users = get_collection("users")


class UserModel(BaseModel):
    userId: str
    username: str
    email: str
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    imageKey: Optional[str] = None


class CreateUserRequest(BaseModel):
    username: str
    email: str
    imageKey: Optional[str] = None


class UpdateUserRequest(BaseModel):
    userId: str
    username: Optional[str] = None
    email: Optional[str] = None
    imageKey: Optional[str] = None


class DeleteUserRequest(BaseModel):
    userId: str


class PublicUserModel(BaseModel):
    userId: str
    username: str
    email: str
    created: datetime
    updated: datetime
    imageKey: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class GetUserRequest(BaseModel):
    userId: str
    authorized: bool = False
