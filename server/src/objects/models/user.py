from sqlalchemy import (
    Column,
    String,
    Integer,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from src.db.pg import Base
from src.utils.date import now
import re


class User(Base):
    __tablename__ = "users"

    userId = Column(String(100), primary_key=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    created = Column(String(50), nullable=False, default=now)
    updated = Column(String(50), nullable=False, default=now)
    fullName = Column(String(255), nullable=True)
    profilePictureUrl = Column(String(500), nullable=True)
    giteaUserId = Column(Integer, nullable=True, unique=True)
    giteaTokenEncrypted = Column(String(1000), nullable=True)
    apiKey = Column(String(100), nullable=True, unique=True)

    # relationships
    owned_agents = relationship(
        "Agent", back_populates="owner", cascade="all, delete-orphan"
    )
    stars = relationship("Star", back_populates="user", cascade="all, delete-orphan")
    forks = relationship("Fork", back_populates="user", cascade="all, delete-orphan")
    contributions = relationship(
        "Contributor",
        foreign_keys="[Contributor.userId]",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sent_invitations = relationship(
        "Contributor",
        foreign_keys="[Contributor.invitedBy]",
        cascade="all, delete-orphan",
    )

    # computed properties
    @hybrid_property
    def agents_count(self):
        return len(self.owned_agents)

    @hybrid_property
    def stars_given_count(self):
        return len(self.stars)

    @hybrid_property
    def forks_created_count(self):
        return len(self.forks)

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
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email cannot be empty")

        email = email.lower().strip()

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            raise ValueError("Invalid email format")

        return email

    @validates("profilePictureUrl")
    def validate_profile_picture_url(self, key, url):
        if url and not re.match(r"^https?://", url):
            raise ValueError("Profile picture URL must start with http:// or https://")
        return url

    @validates("giteaUserId")
    def validate_gitea_user_id(self, key, gitea_user_id):
        if gitea_user_id is not None and gitea_user_id <= 0:
            raise ValueError("Gitea user ID must be positive")
        return gitea_user_id

    # table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "length(username) >= 3 AND length(username) <= 50",
            name="check_username_length",
        ),
        CheckConstraint("username ~ '^[a-zA-Z0-9_-]+$'", name="check_username_format"),
        CheckConstraint(
            "length(email) >= 5 AND length(email) <= 255", name="check_email_length"
        ),
        CheckConstraint("email ~ '^[^@]+@[^@]+\\.[^@]+$'", name="check_email_format"),
        CheckConstraint(
            '"fullName" IS NULL OR length("fullName") <= 255',
            name="check_fullname_length",
        ),
        CheckConstraint(
            '"profilePictureUrl" IS NULL OR "profilePictureUrl" ~ \'^https?://\'',
            name="check_profile_url_format",
        ),
        CheckConstraint(
            '"giteaUserId" IS NULL OR "giteaUserId" > 0',
            name="check_gitea_user_id_positive",
        ),
        Index("idx_user_created", "created"),
        Index("idx_user_updated", "updated"),
        Index("idx_user_fullname", "fullName"),
        Index("idx_user_gitea_id", "giteaUserId"),
    )

    def __repr__(self):
        return f"<User(userId='{self.userId}', username='{self.username}', email='{self.email}')>"
