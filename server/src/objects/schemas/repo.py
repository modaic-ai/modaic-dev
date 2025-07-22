from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, List
from src.utils.date import now

Visibility = Literal["private", "public"]


class RepoSchema(BaseModel):
    repoId: str
    name: str
    description: str
    adminId: str  # reference to the user who created it for now
    created: str = Field(default_factory=lambda: now())
    updated: str = Field(default_factory=lambda: now())
    visibility: Visibility = "private"
    stars: int = 0
    forks: int = 0
    imageKeys: List[str] = []
    forkedFrom: Optional[str] = None

    class Config:
        orm_mode = True


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


class PublicRepoSchema(BaseModel):  # what other people are allowed to see
    name: str
    description: str
    visibility: Visibility
    adminId: str
    created: str
    updated: str
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


class StarRequest(BaseModel):
    repoId: str
    userId: str


class StarSchema(BaseModel):
    starId: str
    repoId: str
    userId: str
    created: str = Field(default_factory=lambda: now())


class ForkRequest(BaseModel):
    repoId: str
    userId: str


class ForkSchema(BaseModel):
    forkId: str
    repoId: str
    userId: str
    created: str = Field(default_factory=lambda: now())


class ImageKeySchema(BaseModel):
    imageKeyId: str
    repoId: str
    imageKey: str
    created: str = Field(default_factory=lambda: now())


class RepoTagSchema(BaseModel):
    tagId: str
    repoId: str
    tag: str
    created: str = Field(default_factory=lambda: now())
