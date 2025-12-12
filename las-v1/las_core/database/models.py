"""
Database Models for LAS.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Database setup is provided by services.db.postgres

class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, user, read-only
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationship
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_active_role', 'is_active', 'role'),
        Index('idx_user_email_active', 'email', 'is_active'),
    )

class UserSession(Base):
    """User session for tracking active tokens."""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="sessions")
    
    # Indexes for session lookups and cleanup
    __table_args__ = (
        Index('idx_session_user_expires', 'user_id', 'expires_at'),
        Index('idx_session_token', 'refresh_token'),
        Index('idx_session_expires', 'expires_at'),  # For cleanup queries
    )

# Pydantic models for API
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserPreference(BaseModel):
    key: str
    value: str

class ModelSelection(BaseModel):
    provider: str
    model: str
    base_url: Optional[str] = None

class PreferencesResponse(BaseModel):
    preferences: dict[str, str]

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

# Initialization handled in services.db.postgres.init_db
