import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from src.db.db import Base


class FileModel(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_downloadable = Column(Boolean, default=True)
    size = Column(Integer)
