"""
Authentication Middleware - FastAPI dependencies for protected routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from services.auth_service import get_auth_service
from database.models import get_db, User
from sqlalchemy.orm import Session

security = HTTPBearer()

class AuthMiddleware:
    """Middleware for handling authentication."""
    
    def __init__(self):
        self.auth_service = get_auth_service()
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """
        Validate JWT token and return current user.
        Use as dependency: user = Depends(auth_middleware.get_current_user)
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        token = credentials.credentials
        payload = self.auth_service.verify_token(token, token_type="access")
        
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            raise credentials_exception
        
        return user
    
    async def get_current_active_user(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Get current active user (convenience method)."""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    
    async def require_role(
        self,
        required_role: str,
        current_user: User = Depends(get_current_user)
    ):
        """
        Require specific role.
        Usage: Depends(lambda: auth_middleware.require_role("admin"))
        """
        role_hierarchy = {"admin": 3, "user": 2, "read-only": 1}
        
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return current_user
    
    async def require_admin(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Require admin role."""
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user

# Singleton instance
_auth_middleware: Optional[AuthMiddleware] = None

def get_auth_middleware() -> AuthMiddleware:
    """Get or create AuthMiddleware instance."""
    global _auth_middleware
    if _auth_middleware is None:
        _auth_middleware = AuthMiddleware()
    return _auth_middleware

# Convenience functions for route dependencies
async def require_auth(current_user: User = Depends(get_auth_middleware().get_current_user)) -> User:
    """Shorthand dependency for requiring authentication."""
    return current_user

async def require_admin_auth(current_user: User = Depends(get_auth_middleware().require_admin)) -> User:
    """Shorthand dependency for requiring admin authentication."""
    return current_user
