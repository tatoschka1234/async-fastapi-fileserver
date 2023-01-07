import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.db import Base


class FileModel(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    path = Column(String(500), nullable=False)
    created_by = Column(UUID(as_uuid=True),
                        ForeignKey('users.id', ondelete="CASCADE"),
                        nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_downloadable = Column(Boolean, default=True)
    size = Column(Integer)
    user = relationship("UserModel", back_populates="files")
