"""
Role-Based Access Control (RBAC) - Multi-user access control system.
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime
from enum import Enum
import json
import secrets

class Role(str, Enum):
    """User roles."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class Permission(str, Enum):
    """System permissions."""
    # Agent control
    AGENT_CREATE = "agent.create"
    AGENT_DELETE = "agent.delete"
    AGENT_EXECUTE = "agent.execute"
    
    # Tool permissions
    TOOL_CODE = "tool.code"
    TOOL_FILE_READ = "tool.file.read"
    TOOL_FILE_WRITE = "tool.file.write"
    TOOL_NETWORK = "tool.network"
    TOOL_DATABASE = "tool.database"
    
    # System permissions
    SYSTEM_CONFIG = "system.config"
    SYSTEM_USERS = "system.users"
    SYSTEM_AUDIT = "system.audit"
    
    # Approval permissions
    APPROVAL_APPROVE = "approval.approve"
    APPROVAL_REQUEST = "approval.request"

# Role-to-permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Admins have all permissions
        *list(Permission)
    },
    Role.DEVELOPER: {
        Permission.AGENT_CREATE,
        Permission.AGENT_EXECUTE,
        Permission.TOOL_CODE,
        Permission.TOOL_FILE_READ,
        Permission.TOOL_FILE_WRITE,
        Permission.TOOL_NETWORK,
        Permission.TOOL_DATABASE,
        Permission.APPROVAL_REQUEST,
        Permission.SYSTEM_AUDIT,  # Can view audit logs
    },
    Role.VIEWER: {
        Permission.AGENT_EXECUTE,  # Can run agents
        Permission.TOOL_FILE_READ,  # Read-only
        Permission.SYSTEM_AUDIT,  # View audit logs
    }
}

class User:
    """Represents a user."""
    
    def __init__(self, username: str, role: Role, api_key: Optional[str] = None):
        self.username = username
        self.role = role
        self.api_key = api_key or self._generate_api_key()
        self.created_at = datetime.now()
        self.last_login: Optional[datetime] = None
    
    def _generate_api_key(self) -> str:
        """Generate secure API key."""
        return f"las_{secrets.token_urlsafe(32)}"
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in ROLE_PERMISSIONS.get(self.role, set())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "username": self.username,
            "role": self.role.value,
            "api_key": self.api_key,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class RBACSystem:
    """Role-Based Access Control system."""
    
    def __init__(self, storage_dir: str = "data/rbac"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> username
        
        self.load_users()
        
        # Create default admin if no users exist
        if not self.users:
            self.create_user("admin", Role.ADMIN)
    
    def load_users(self):
        """Load users from storage."""
        users_file = self.storage_dir / "users.json"
        if users_file.exists():
            try:
                with open(users_file, 'r') as f:
                    data = json.load(f)
                    for user_data in data:
                        user = User(
                            username=user_data["username"],
                            role=Role(user_data["role"]),
                            api_key=user_data["api_key"]
                        )
                        user.created_at = datetime.fromisoformat(user_data["created_at"])
                        if user_data.get("last_login"):
                            user.last_login = datetime.fromisoformat(user_data["last_login"])
                        
                        self.users[user.username] = user
                        self.api_keys[user.api_key] = user.username
            except Exception as e:
                print(f"Failed to load users: {e}")
    
    def save_users(self):
        """Save users to storage."""
        users_file = self.storage_dir / "users.json"
        try:
            data = [user.to_dict() for user in self.users.values()]
            with open(users_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save users: {e}")
    
    def create_user(self, username: str, role: Role) -> User:
        """Create a new user."""
        if username in self.users:
            raise ValueError(f"User {username} already exists")
        
        user = User(username=username, role=role)
        self.users[username] = user
        self.api_keys[user.api_key] = username
        
        self.save_users()
        
        # Log to audit trail
        from security.audit_logger import get_audit_logger, AuditEventType
        audit = get_audit_logger()
        audit.log(
            event_type=AuditEventType.DATA_ACCESS,
            action="create_user",
            details={"username": username, "role": role.value}
        )
        
        return user
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username not in self.users:
            return False
        
        user = self.users[username]
        del self.api_keys[user.api_key]
        del self.users[username]
        
        self.save_users()
        
        # Log to audit trail
        from security.audit_logger import get_audit_logger, AuditEventType
        audit = get_audit_logger()
        audit.log(
            event_type=AuditEventType.DATA_ACCESS,
            action="delete_user",
            details={"username": username}
        )
        
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.users.get(username)
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key."""
        username = self.api_keys.get(api_key)
        return self.users.get(username) if username else None
    
    def list_users(self) -> List[User]:
        """List all users."""
        return list(self.users.values())
    
    def check_permission(self, api_key: str, permission: Permission) -> bool:
        """Check if API key has permission."""
        user = self.get_user_by_api_key(api_key)
        if not user:
            return False
        
        return user.has_permission(permission)
    
    def update_last_login(self, username: str):
        """Update user's last login time."""
        user = self.users.get(username)
        if user:
            user.last_login = datetime.now()
            self.save_users()
    
    def regenerate_api_key(self, username: str) -> Optional[str]:
        """Regenerate API key for a user."""
        user = self.users.get(username)
        if not user:
            return None
        
        # Remove old API key
        del self.api_keys[user.api_key]
        
        # Generate new API key
        user.api_key = user._generate_api_key()
        self.api_keys[user.api_key] = username
        
        self.save_users()
        return user.api_key

# Create singleton instance
_rbac_system: Optional[RBACSystem] = None

def get_rbac_system() -> RBACSystem:
    """Get or create RBACSystem instance."""
    global _rbac_system
    if _rbac_system is None:
        _rbac_system = RBACSystem()
    return _rbac_system

# Middleware decorator for permission checking
def require_permission(permission: Permission):
    """Decorator to require permission for endpoint."""
    def decorator(func):
        async def wrapper(*args, api_key: str = None, **kwargs):
            rbac = get_rbac_system()
            if not api_key or not rbac.check_permission(api_key, permission):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
