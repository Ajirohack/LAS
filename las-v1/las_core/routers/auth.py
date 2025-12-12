"""
Authentication Router - Login, register, logout endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, delete
from datetime import datetime, timedelta

from database.models import (
    User, UserSession, UserCreate, UserResponse, TokenResponse,
)
from services.db.postgres import get_db
from services.auth_service import get_auth_service
from middleware.auth_middleware import require_auth

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    auth_service = get_auth_service()
    
    try:
        # Check if user exists
        result = await db.execute(
            select(User).where(
                or_(User.username == user_data.username, User.email == user_data.email)
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Validate password
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=auth_service.get_password_hash(user_data.password),
            role=user_data.role if user_data.role in ["admin", "user", "read-only"] else "user",
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    username: str,
    password: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login and receive JWT tokens."""
    auth_service = get_auth_service()
    
    # Authenticate user
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth_service.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "username": user.username, "role": user.role}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.id}
    )
    
    # Create session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(session)
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    auth_service = get_auth_service()
    
    # Verify refresh token
    payload = auth_service.verify_token(refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if session exists
    result = await db.execute(select(UserSession).where(UserSession.refresh_token == refresh_token))
    session = result.scalar_one_or_none()
    
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid"
        )
    
    user = session.user
    
    # Create new access token
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "username": user.username, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    access_token: str,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    """Logout and invalidate tokens."""
    auth_service = get_auth_service()
    
    # Add token to blacklist
    auth_service.blacklist_token(access_token)
    
    # Delete all user sessions
    await db.execute(delete(UserSession).where(UserSession.user_id == current_user.id))
    await db.commit()
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """Get current authenticated user information."""
    return current_user

@router.put("/me/password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    auth_service = get_auth_service()
    
    # Verify current password
    if not auth_service.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    # Update password
    current_user.hashed_password = auth_service.get_password_hash(new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}
