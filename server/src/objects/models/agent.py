from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    CheckConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from src.db.pg import Base
from src.utils.date import now
from sqlalchemy.ext.hybrid import hybrid_property


class Agent(Base):
    __tablename__ = "agents"

    agentId = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=False)
    adminId = Column(String(100), ForeignKey("users.userId"), nullable=False)
    configYaml = Column(String(50000), nullable=False, default="")
    readmeContent = Column(String(50000), nullable=False, default="")
    version = Column(String(20), nullable=False, default="1.0.0")
    lastMirrored = Column(String, nullable=True)
    created = Column(String, nullable=False, default=now)
    updated = Column(String, nullable=False, default=now, onupdate=now)
    visibility = Column(String(20), nullable=False, default="private")

    # relationships
    owner = relationship("User", back_populates="owned_agents")
    contributors = relationship("Contributor", back_populates="agent")
    star_records = relationship(
        "Star",
        foreign_keys="[Star.agentId]",  # Original agent being starred
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    fork_records = relationship(
        "Fork",
        foreign_keys="[Fork.agentId]",  # Original agent being forked
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    image_keys = relationship(
        "ImageKey",
        foreign_keys="[ImageKey.agentId]",  # Original agent's image keys
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    agent_tags = relationship(
        "AgentTag",
        foreign_keys="[AgentTag.agentId]",  # Original agent's tags
        back_populates="agent",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def stars_count(self):
        return len(self.star_records)

    @hybrid_property
    def forks_count(self):
        return len(self.fork_records)

    @hybrid_property
    def tags(self):
        return [tag.tag for tag in self.agent_tags]

    __table_args__ = (
        CheckConstraint("visibility IN ('private', 'public')", name="check_visibility"),
        CheckConstraint(
            "version ~ '^[0-9]+\\.[0-9]+\\.[0-9]+$'", name="check_version_format"
        ),
        Index("idx_agent_admin_visibility", "adminId", "visibility"),
        Index("idx_agent_created", "created"),
        Index("idx_agent_visibility_created", "visibility", "created"),
    )

    def __repr__(self):
        return f"<Agent(agentId='{self.agentId}', name='{self.name}')>"


class Star(Base):
    __tablename__ = "stars"

    starId = Column(String(100), primary_key=True)
    userId = Column(String(100), ForeignKey("users.userId"), nullable=False)
    agentId = Column(
        String(100), ForeignKey("agents.agentId", ondelete="CASCADE"), nullable=False
    )
    created = Column(String, nullable=False, default=now)

    # relationships
    user = relationship("User", back_populates="stars")
    agent = relationship("Agent", back_populates="star_records")

    # constraints
    __table_args__ = (
        UniqueConstraint("userId", "agentId", name="unique_user_agent_star"),
        Index("idx_star_agent", "agentId"),
        Index("idx_star_user", "userId"),
    )

    def __repr__(self):
        return f"<Star(starId='{self.starId}', userId='{self.userId}', agentId='{self.agentId}')>"


class Fork(Base):
    __tablename__ = "forks"

    forkId = Column(String(100), primary_key=True)
    userId = Column(String(100), ForeignKey("users.userId"), nullable=False)
    agentId = Column(
        String(100), ForeignKey("agents.agentId", ondelete="CASCADE"), nullable=False
    )
    forkedAgentId = Column(
        String(100), ForeignKey("agents.agentId"), nullable=False
    )  # new forked agent
    created = Column(String, nullable=False, default=now)

    # relationships
    user = relationship("User", back_populates="forks")
    agent = relationship(
        "Agent", foreign_keys=[agentId], back_populates="fork_records"
    )  # original agent
    forked_agent = relationship(
        "Agent", foreign_keys=[forkedAgentId], overlaps="forks"
    )  # new forked agent

    # constraints
    __table_args__ = (
        UniqueConstraint("userId", "agentId", name="unique_user_agent_fork"),
        Index("idx_fork_agent", "agentId"),
        Index("idx_fork_user", "userId"),
        Index("idx_fork_forked_agent", "forkedAgentId"),
    )

    def __repr__(self):
        return f"<Fork(forkId='{self.forkId}', userId='{self.userId}', agentId='{self.agentId}')>"


class ImageKey(Base):
    __tablename__ = "image_keys"

    imageKeyId = Column(String(100), primary_key=True)
    agentId = Column(
        String(100), ForeignKey("agents.agentId", ondelete="CASCADE"), nullable=False
    )
    imageKey = Column(String(500), nullable=False)
    created = Column(String, nullable=False, default=now)

    # relationships
    agent = relationship("Agent", back_populates="image_keys")

    # constraints
    __table_args__ = (
        Index("idx_image_key_agent", "agentId"),
        UniqueConstraint("agentId", "imageKey", name="unique_agent_image_key"),
    )

    def __repr__(self):
        return f"<ImageKey(imageKeyId='{self.imageKeyId}', agentId='{self.agentId}')>"


class AgentTag(Base):
    __tablename__ = "agent_tags"

    tagId = Column(String(100), primary_key=True)
    agentId = Column(
        String(100), ForeignKey("agents.agentId", ondelete="CASCADE"), nullable=False
    )
    tag = Column(String(50), nullable=False)
    created = Column(String, nullable=False, default=now)

    # relationships
    agent = relationship("Agent", back_populates="agent_tags")

    # constraints
    __table_args__ = (
        UniqueConstraint("agentId", "tag", name="unique_agent_tag"),
        Index("idx_agent_tag_agent", "agentId"),
        Index("idx_agent_tag_tag", "tag"),
        CheckConstraint("length(tag) > 0", name="check_tag_not_empty"),
    )

    def __repr__(self):
        return f"<AgentTag(tagId='{self.tagId}', agentId='{self.agentId}', tag='{self.tag}')>"
