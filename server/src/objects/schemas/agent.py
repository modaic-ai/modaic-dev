from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from src.utils.date import now


class AgentSchema(BaseModel):
    agentId: str
    repoId: str
    name: str
    description: str
    adminId: str
    configYaml: Dict[str, Any] = {}
    readmeContent: str = ""
    tags: List[str] = []
    version: str = "1.0.0"
    lastMirrored: str = Field(default_factory=lambda: now())
    created: str = Field(default_factory=lambda: now())
    updated: str = Field(default_factory=lambda: now())

    class Config:
        orm_mode = True


class CreateAgentRequest(BaseModel):
    name: str
    description: str
    repoId: str
    adminId: str
    configYaml: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []


class UpdateAgentRequest(BaseModel):
    agentId: str
    name: Optional[str] = None
    description: Optional[str] = None
    configYaml: Optional[Dict[str, Any]] = None
    readmeContent: Optional[str] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None
    updated: str = Field(default_factory=lambda: now())


class PublicAgentSchema(BaseModel):
    agentId: str
    name: str
    description: str
    adminId: str
    configYaml: Dict[str, Any]
    readmeContent: str
    tags: List[str]
    version: str
    created: str
    updated: str
    lastMirrored: str

    model_config = ConfigDict(extra="ignore")
