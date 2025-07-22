from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.db.pg import Base
from src.utils.date import now


class Agent(Base):
    __tablename__ = "agents"

    agentId = Column(String, primary_key=True, index=True)
    repoId = Column(String, ForeignKey("repos.repoId"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    adminId = Column(String, ForeignKey("users.userId"), nullable=False)
    configYaml = Column(String, nullable=False)
    readmeContent = Column(String, nullable=False)
    tags = Column(JSON, nullable=False, default=list)
    version = Column(String, nullable=False)
    lastMirrored = Column(String, nullable=False)
    created = Column(String, nullable=False, default=now)
    updated = Column(String, nullable=False, default=now, onupdate=now)

    repo = relationship("Repo", back_populates="agents")
    admin_user = relationship("User", back_populates="agents")
