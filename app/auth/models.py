from sqlalchemy import Column, Integer, String, Enum, Boolean, ForeignKey, DateTime
from app.core.database import Base
from datetime import datetime,timedelta
from sqlalchemy.orm import relationship
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)

    reset_tokens = relationship("PasswordResetToken", back_populates="user")
    products = relationship("Product", back_populates="owner")


class PasswordResetToken(Base):
    __tablename__ = "passwordresettokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True,nullable=False)
    expiration_time = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=15))
    used = Column(Boolean, default=False)

    user = relationship("User", back_populates="reset_tokens")
