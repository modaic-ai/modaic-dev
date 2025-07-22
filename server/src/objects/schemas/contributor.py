from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from src.utils.date import now

class ContributorSchema(BaseModel):
    contributorId: str
    userId: Optional[str] = None
    username: Optional[str] = None
    email: str
    repoId: str
    accessLevel: Literal["read", "write", "admin"] = "read"
    invitedAt: str = Field(default_factory=lambda: now())
    acceptedAt: Optional[str] = None
    pending: bool = True
    invitedBy: str

    class Config:
        orm_mode = True


class PublicContributorSchema(BaseModel):
    contributorId: str
    userId: Optional[str] = None
    username: Optional[str] = None
    repoId: str
    accessLevel: Literal["read", "write", "admin"] = "read"
    pending: bool = True

    model_config = ConfigDict(extra="ignore")
