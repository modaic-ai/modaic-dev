from pydantic import BaseModel
from datetime import datetime
from pydantic import Field
from pydantic import ConfigDict
from pytz import UTC
from typing import Literal, Optional, List
from src.db.mongo import get_collection

Repos = get_collection("repos")
Visibility = Literal["private", "public"]


class RepoModel(BaseModel):
    repoId: str
    name: str
    description: str
    adminId: str  # reference to the user who created it for now
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    visibility: Visibility = "private"
    stars: int = 0
    forks: int = 0
    imageKeys: List[str] = []
    forkedFrom: Optional[str] = None


class CreateRepoRequest(BaseModel):
    name: str
    description: str
    visibility: Visibility = "private"
    adminId: str


class UpdateRepoRequest(BaseModel):
    repoId: str
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[Visibility] = None
    adminId: Optional[str] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    imageKeys: Optional[List[str]] = None
    forkedFrom: Optional[str] = None


class PublicRepoModel(BaseModel):  # what other people are allowed to see
    name: str
    description: str
    visibility: Visibility
    adminId: str
    created: datetime
    updated: datetime
    stars: int
    forks: int
    imageKeys: List[str]
    forkedFrom: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class DeleteRepoRequest(BaseModel):
    repoId: str


class GetRepoRequest(BaseModel):
    repoId: str
    authorized: bool = False
