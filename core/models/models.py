from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, DateTime, Numeric, UniqueConstraint, func
from sqlalchemy.orm import relationship
from .base import Base


roles_enum = ENUM("admin", "moderator", "user", name="user_roles", create_type=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    avatar = Column(String)
    google_id = Column(String, unique=True, nullable=True)
    telegram_id = Column(String, unique=True, nullable=True)
    steam_id = Column(String, unique=True, nullable=True)
    role = Column(roles_enum, nullable=False, default="user")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

