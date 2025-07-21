from pydantic import BaseModel, Field
from datetime import datetime
from pytz import UTC
from typing import Optional, List, Dict, Any
from src.db.mongo import get_collection

Agents = get_collection("agents")


class AgentModel(BaseModel):
    agentId: str
    repoId: str
    name: str
    description: str
    adminId: str
    configYaml: Dict[str, Any] = {}
    readmeContent: str = ""
    tags: List[str] = []
    version: str = "1.0.0"
    lastMirrored: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


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


class PublicAgentModel(BaseModel):
    agentId: str
    name: str
    description: str
    adminId: str
    configYaml: Dict[str, Any]
    readmeContent: str
    tags: List[str]
    version: str
    created: datetime
    updated: datetime
    lastMirrored: datetime
