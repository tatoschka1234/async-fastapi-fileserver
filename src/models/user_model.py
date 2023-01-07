import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.db.db import Base
from src.core.config import app_settings


class UserModel(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(app_settings.UNANE_MAX_LEN), nullable=False)
    psw_hash = Column(String(300), nullable=False)
    files = relationship(
        "FileModel", back_populates="user", passive_deletes=True
    )


