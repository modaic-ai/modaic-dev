from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.db.pg import Base
from src.utils.date import now


class Contributor(Base):
    __tablename__ = "contributors"

    contributorId = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.userId"), nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    repoId = Column(String, ForeignKey("repos.repoId"), nullable=False)
    accessLevel = Column(String, nullable=False)
    invitedAt = Column(String, nullable=False, default=now)
    acceptedAt = Column(String, nullable=False)
    pending = Column(Boolean, nullable=False)
    invitedBy = Column(String, nullable=False)

    user = relationship("User", back_populates="contributions")
    repo = relationship("Repo", back_populates="contributors")