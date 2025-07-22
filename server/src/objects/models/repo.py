from sqlalchemy import Column, String, ForeignKey, Integer, JSON, DateTime, text
from sqlalchemy.orm import relationship
from src.db.pg import Base
from src.utils.date import now


class Repo(Base):
    __tablename__ = "repos"

    repoId = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    adminId = Column(String, ForeignKey("users.userId"), nullable=False)
    created = Column(String, nullable=False, default=now)
    updated = Column(String, nullable=False, default=now, onupdate=now)
    visibility = Column(String, nullable=False, default="private")
    
    # counters (keep these as columns)
    stars = Column(Integer, nullable=False, default=0)
    forks = Column(Integer, nullable=False, default=0)

    # relationships
    owner = relationship("User", back_populates="owned_repos")
    agents = relationship("Agent", back_populates="repo")
    contributors = relationship("Contributor", back_populates="repo")
    star_records = relationship("Star", back_populates="repo")
    fork_records = relationship("Fork", back_populates="repo")
    image_keys = relationship("ImageKey", back_populates="repo")
    repo_tags = relationship("RepoTag", back_populates="repo")



class Star(Base):
    __tablename__ = "stars"

    starId = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.userId"), nullable=False)
    repoId = Column(String, ForeignKey("repos.repoId"), nullable=False)
    created = Column(String, nullable=False, default=now)

    user = relationship("User", back_populates="stars")  # Singular
    repo = relationship("Repo", back_populates="star_records")  # Fixed


class Fork(Base):
    __tablename__ = "forks"

    forkId = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.userId"), nullable=False)
    repoId = Column(String, ForeignKey("repos.repoId"), nullable=False)
    created = Column(String, nullable=False, default=now)

    user = relationship("User", back_populates="forks")  # Singular
    repo = relationship("Repo", back_populates="fork_records")  # Plural


class ImageKey(Base):
    __tablename__ = "image_keys"

    imageKeyId = Column(String, primary_key=True, index=True)
    repoId = Column(String, ForeignKey("repos.repoId"), nullable=False)
    imageKey = Column(String, nullable=False)
    created = Column(String, nullable=False, default=now)

    repo = relationship("Repo", back_populates="image_keys") 


class RepoTag(Base):
    __tablename__ = "repo_tags"

    tagId = Column(String, primary_key=True, index=True)
    repoId = Column(String, ForeignKey("repos.repoId"), nullable=False)
    tag = Column(String, nullable=False)
    created = Column(String, nullable=False, default=now)

    repo = relationship("Repo", back_populates="repo_tags")
