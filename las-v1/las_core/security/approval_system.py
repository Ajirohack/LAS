"""
Approval System - Human-in-the-Loop controls for sensitive operations.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

class ActionCategory(str, Enum):
    """Categories of actions requiring approval."""
    CODE_EXECUTION = "code_execution"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    NETWORK_REQUEST = "network_request"
    DATABASE_WRITE = "database_write"
    SYSTEM_COMMAND = "system_command"

class ApprovalStatus(str, Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

class ApprovalRequest:
    """Represents an approval request."""
    
    def __init__(self, action_category: ActionCategory, action_description: str,
                 details: Dict[str, Any], agent: Optional[str] = None,
                 timeout_minutes: int = 30):
        self.id = str(uuid.uuid4())
        self.action_category = action_category
        self.action_description = action_description
        self.details = details
        self.agent = agent
        self.status = ApprovalStatus.PENDING
        self.created_at = datetime.now()
        self.timeout_at = datetime.now() + timedelta(minutes=timeout_minutes)
        self.responded_at: Optional[datetime] = None
        self.response_user: Optional[str] = None
        self.response_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "action_category": self.action_category.value,
            "action_description": self.action_description,
            "details": self.details,
            "agent": self.agent,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "timeout_at": self.timeout_at.isoformat(),
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "response_user": self.response_user,
            "response_message": self.response_message
        }

class ApprovalSystem:
    """
    Manages approval requests for sensitive operations.
    
    Features:
    - Request approval before executing sensitive actions
    - Timeout for pending requests
    - Audit trail integration
    - Configurable action categories
    """
    
    def __init__(self, storage_dir: str = "data/approvals"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.load_pending()
    
    def load_pending(self):
        """Load pending requests from storage."""
        pending_file = self.storage_dir / "pending.json"
        if pending_file.exists():
            try:
                with open(pending_file, 'r') as f:
                    data = json.load(f)
                    for req_data in data:
                        req = ApprovalRequest(
                            action_category=ActionCategory(req_data["action_category"]),
                            action_description=req_data["action_description"],
                            details=req_data["details"],
                            agent=req_data.get("agent")
                        )
                        req.id = req_data["id"]
                        req.status = ApprovalStatus(req_data["status"])
                        req.created_at = datetime.fromisoformat(req_data["created_at"])
                        req.timeout_at = datetime.fromisoformat(req_data["timeout_at"])
                        
                        self.pending_requests[req.id] = req
            except Exception as e:
                print(f"Failed to load pending requests: {e}")
    
    def save_pending(self):
        """Save pending requests to storage."""
        pending_file = self.storage_dir / "pending.json"
        try:
            data = [req.to_dict() for req in self.pending_requests.values()]
            with open(pending_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save pending requests: {e}")
    
    def request_approval(self, action_category: ActionCategory,
                        action_description: str,
                        details: Dict[str, Any],
                        agent: Optional[str] = None,
                        timeout_minutes: int = 30) -> ApprovalRequest:
        """
        Request approval for a sensitive action.
        
        Args:
            action_category: Category of action
            action_description: Human-readable description
            details: Additional details
            agent: Agent identifier
            timeout_minutes: Minutes to wait before timeout
        
        Returns:
            ApprovalRequest object
        """
        request = ApprovalRequest(
            action_category=action_category,
            action_description=action_description,
            details=details,
            agent=agent,
            timeout_minutes=timeout_minutes
        )
        
        self.pending_requests[request.id] = request
        self.save_pending()
        
        # Log to audit trail
        from security.audit_logger import get_audit_logger, AuditEventType
        audit_logger = get_audit_logger()
        audit_logger.log(
            event_type=AuditEventType.APPROVAL_REQUEST,
            action=f"request_{action_category.value}",
            details={"request_id": request.id, **details},
            agent=agent
        )
        
        return request
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID."""
        return self.pending_requests.get(request_id)
    
    def approve(self, request_id: str, user: str, message: Optional[str] = None) -> bool:
        """
        Approve a request.
        
        Args:
            request_id: Request ID
            user: User approving
            message: Optional message
        
        Returns:
            Success boolean
        """
        request = self.pending_requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        request.status = ApprovalStatus.APPROVED
        request.responded_at = datetime.now()
        request.response_user = user
        request.response_message = message
        
        self.save_pending()
        
        # Log to audit trail
        from security.audit_logger import get_audit_logger, AuditEventType
        audit_logger = get_audit_logger()
        audit_logger.log(
            event_type=AuditEventType.APPROVAL_RESPONSE,
            action="approve",
            details={"request_id": request_id, "user": user, "message": message},
            agent=request.agent
        )
        
        return True
    
    def reject(self, request_id: str, user: str, message: Optional[str] = None) -> bool:
        """
        Reject a request.
        
        Args:
            request_id: Request ID
            user: User rejecting
            message: Optional message
        
        Returns:
            Success boolean
        """
        request = self.pending_requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        request.status = ApprovalStatus.REJECTED
        request.responded_at = datetime.now()
        request.response_user = user
        request.response_message = message
        
        self.save_pending()
        
        # Log to audit trail
        from security.audit_logger import get_audit_logger, AuditEventType
        audit_logger = get_audit_logger()
        audit_logger.log(
            event_type=AuditEventType.APPROVAL_RESPONSE,
            action="reject",
            details={"request_id": request_id, "user": user, "message": message},
            agent=request.agent
        )
        
        return True
    
    def check_timeouts(self):
        """Check and mark timed-out requests."""
        now = datetime.now()
        for request in list(self.pending_requests.values()):
            if request.status == ApprovalStatus.PENDING and now > request.timeout_at:
                request.status = ApprovalStatus.TIMEOUT
                request.responded_at = now
        
        self.save_pending()
    
    def list_pending(self) -> List[ApprovalRequest]:
        """List all pending requests."""
        self.check_timeouts()
        return [r for r in self.pending_requests.values() if r.status == ApprovalStatus.PENDING]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get approval system statistics."""
        total = len(self.pending_requests)
        by_status = {}
        by_category = {}
        
        for req in self.pending_requests.values():
            by_status[req.status.value] = by_status.get(req.status.value, 0) + 1
            by_category[req.action_category.value] = by_category.get(req.action_category.value, 0) + 1
        
        return {
            "total_requests": total,
            "by_status": by_status,
            "by_category": by_category
        }

# Create singleton instance
_approval_system: Optional[ApprovalSystem] = None

def get_approval_system() -> ApprovalSystem:
    """Get or create ApprovalSystem instance."""
    global _approval_system
    if _approval_system is None:
        _approval_system = ApprovalSystem()
    return _approval_system
