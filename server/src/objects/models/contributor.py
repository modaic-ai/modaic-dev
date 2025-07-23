from sqlalchemy import (
    Boolean,
    Column,
    String,
    ForeignKey,
    CheckConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, validates
from src.db.pg import Base
from src.utils.date import now
import re


class Contributor(Base):
    __tablename__ = "contributors"

    contributorId = Column(String(100), primary_key=True)
    userId = Column(
        String(100), ForeignKey("users.userId", ondelete="CASCADE"), nullable=False
    )
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    agentId = Column(
        String(100), ForeignKey("agents.agentId", ondelete="CASCADE"), nullable=False
    )
    accessLevel = Column(String(20), nullable=False, default="read")
    invitedAt = Column(String(50), nullable=False, default=now)
    acceptedAt = Column(String(50), nullable=True)
    pending = Column(Boolean, nullable=False, default=True)
    invitedBy = Column(String(100), ForeignKey("users.userId"), nullable=False)

    # relationships
    user = relationship("User", foreign_keys=[userId], back_populates="contributions")
    agent = relationship("Agent", back_populates="contributors")
    inviter = relationship(
        "User", foreign_keys=[invitedBy], overlaps="sent_invitations"
    )

    # validation methods
    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username cannot be empty")

        username = username.lower().strip()

        if not re.match(r"^[a-zA-Z0-9_-]{3,50}$", username):
            raise ValueError(
                "Username must be 3-50 characters and contain only letters, numbers, hyphens, and underscores"
            )

        return username

    @validates("email")
    def validate_email(self, key: str, email: str):
        if not email:
            raise ValueError("Email cannot be empty")

        email = email.lower().strip()

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            raise ValueError("Invalid email format")

        return email

    @validates("accessLevel")
    def validate_access_level(self, key, access_level):
        valid_levels = ["read", "write", "admin"]
        if access_level not in valid_levels:
            raise ValueError(f"Access level must be one of: {', '.join(valid_levels)}")
        return access_level

    @validates("pending")
    def validate_pending(self, key, pending):
        if pending not in ["true", "false"]:
            raise ValueError("Pending must be 'true' or 'false'")
        return pending

    # helper properties
    @property
    def is_pending(self):
        """Convert string boolean to actual boolean."""
        return self.pending

    @property
    def is_accepted(self):
        """Check if invitation has been accepted."""
        return self.acceptedAt is not None and self.pending == "false"

    # table constraints and indexes
    __table_args__ = (
        # check constraints for data validation
        CheckConstraint(
            "\"accessLevel\" IN ('read', 'write', 'admin')",
            name="check_access_level_valid",
        ),
        CheckConstraint("pending IN ('true', 'false')", name="check_pending_format"),
        CheckConstraint(
            "length(username) >= 3 AND length(username) <= 50",
            name="check_username_length",
        ),
        CheckConstraint("username ~ '^[a-zA-Z0-9_-]+$'", name="check_username_format"),
        CheckConstraint(
            "length(email) >= 5 AND length(email) <= 255", name="check_email_length"
        ),
        CheckConstraint("email ~ '^[^@]+@[^@]+\\.[^@]+$'", name="check_email_format"),
        # unique constraint to prevent duplicate invitations
        UniqueConstraint("userId", "agentId", name="unique_user_agent_contributor"),
        # performance indexes
        Index("idx_contributor_user", "userId"),
        Index("idx_contributor_agent", "agentId"),
        Index("idx_contributor_pending", "pending"),
        Index("idx_contributor_access_level", "accessLevel"),
        Index("idx_contributor_invited_at", "invitedAt"),
        Index("idx_contributor_invited_by", "invitedBy"),
        Index("idx_contributor_email", "email"),
        # Composite indexes for common queries
        Index("idx_contributor_agent_pending", "agentId", "pending"),
        Index("idx_contributor_user_pending", "userId", "pending"),
        Index("idx_contributor_agent_access", "agentId", "accessLevel"),
    )

    def __repr__(self):
        return f"<Contributor(contributorId='{self.contributorId}', username='{self.username}', agentId='{self.agentId}', accessLevel='{self.accessLevel}')>"

    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary with option to include/exclude sensitive fields."""
        data = {
            "contributorId": self.contributorId,
            "userId": self.userId,
            "username": self.username,
            "agentId": self.agentId,
            "accessLevel": self.accessLevel,
            "invitedAt": self.invitedAt,
            "acceptedAt": self.acceptedAt,
            "pending": self.is_pending,
            "invitedBy": self.invitedBy,
        }

        if include_sensitive:
            data["email"] = self.email

        return data

    def to_public_dict(self):
        """Convert to dictionary with only public fields."""
        return {
            "contributorId": self.contributorId,
            "username": self.username,
            "agentId": self.agentId,
            "accessLevel": self.accessLevel,
            "invitedAt": self.invitedAt,
            "acceptedAt": self.acceptedAt,
            "pending": self.is_pending,
        }
