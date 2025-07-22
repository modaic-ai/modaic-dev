from sqlalchemy import Column, String, Integer, DateTime
from src.db.pg import Base
from src.utils.date import now
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    userId = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    created = Column(String, nullable=False, default=now)
    updated = Column(String, nullable=False, default=now, onupdate=now)
    fullName = Column(String, nullable=True)
    profilePictureUrl = Column(String, nullable=True)
    giteaUserId = Column(Integer, nullable=True)
    giteaTokenEncrypted = Column(String, nullable=True)
    apiKey = Column(String, nullable=True)

    # Fixed relationships (one-to-many are plural)
    owned_repos = relationship("Repo", back_populates="owner")
    stars = relationship("Star", back_populates="user")
    forks = relationship("Fork", back_populates="user")
    contributions = relationship("Contributor", back_populates="user")
    agents = relationship("Agent", back_populates="admin_user")

