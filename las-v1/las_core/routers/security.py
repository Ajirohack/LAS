from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from security.audit_logger import get_audit_logger, AuditEventType
from security.approval_system import get_approval_system, ActionCategory
from security.rbac import get_rbac_system, Role, Permission
from security.pii_redactor import get_pii_redactor, SensitivityLevel

router = APIRouter()

# === Audit Log Endpoints ===

@router.get("/audit/logs")
async def query_audit_logs(
    event_type: Optional[str] = None,
    agent: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Query audit logs with filters."""
    try:
        logger = get_audit_logger()
        
        event_type_enum = AuditEventType(event_type) if event_type else None
        
        logs = logger.query(
            event_type=event_type_enum,
            agent=agent,
            limit=limit
        )
        
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/verify")
async def verify_audit_integrity():
    """Verify integrity of audit log chain."""
    try:
        logger = get_audit_logger()
        is_valid = logger.verify_integrity()
        return {"valid": is_valid, "status": "intact" if is_valid else "compromised"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/stats")
async def get_audit_stats():
    """Get audit log statistics."""
    try:
        logger = get_audit_logger()
        return logger.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Approval System Endpoints ===

class ApprovalRequestModel(BaseModel):
    action_category: str
    action_description: str
    details: dict
    agent: Optional[str] = None
    timeout_minutes: int = 30

class ApprovalResponseModel(BaseModel):
    user: str
    message: Optional[str] = None

@router.post("/approvals/request")
async def create_approval_request(request: ApprovalRequestModel):
    """Request approval for a sensitive action."""
    try:
        system = get_approval_system()
        category = ActionCategory(request.action_category)
        
        approval_req = system.request_approval(
            action_category=category,
            action_description=request.action_description,
            details=request.details,
            agent=request.agent,
            timeout_minutes=request.timeout_minutes
        )
        
        return approval_req.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approvals/pending")
async def list_pending_approvals():
    """List all pending approval requests."""
    try:
        system = get_approval_system()
        requests = system.list_pending()
        return {"requests": [r.to_dict() for r in requests]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approvals/{request_id}")
async def get_approval_request(request_id: str):
    """Get specific approval request."""
    try:
        system = get_approval_system()
        request = system.get_request(request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        return request.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approvals/{request_id}/approve")
async def approve_request(request_id: str, response: ApprovalResponseModel):
    """Approve an approval request."""
    try:
        system = get_approval_system()
        success = system.approve(request_id, response.user, response.message)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot approve request")
        return {"status": "approved", "request_id": request_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approvals/{request_id}/reject")
async def reject_request(request_id: str, response: ApprovalResponseModel):
    """Reject an approval request."""
    try:
        system = get_approval_system()
        success = system.reject(request_id, response.user, response.message)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot reject request")
        return {"status": "rejected", "request_id": request_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approvals/stats")
async def get_approval_stats():
    """Get approval system statistics."""
    try:
        system = get_approval_system()
        return system.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === RBAC Endpoints ===

class UserCreateRequest(BaseModel):
    username: str
    role: str

@router.post("/rbac/users")
async def create_user(request: UserCreateRequest):
    """Create a new user."""
    try:
        rbac = get_rbac_system()
        role = Role(request.role)
        user = rbac.create_user(request.username, role)
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rbac/users")
async def list_users():
    """List all users."""
    try:
        rbac = get_rbac_system()
        users = rbac.list_users()
        return {"users": [u.to_dict() for u in users]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rbac/users/{username}")
async def delete_user(username: str):
    """Delete a user."""
    try:
        rbac = get_rbac_system()
        success = rbac.delete_user(username)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "deleted", "username": username}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rbac/users/{username}/regenerate-key")
async def regenerate_api_key(username: str):
    """Regenerate API key for a user."""
    try:
        rbac = get_rbac_system()
        new_key = rbac.regenerate_api_key(username)
        if not new_key:
            raise HTTPException(status_code=404, detail="User not found")
        return {"username": username, "api_key": new_key}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === PII Redaction Endpoints ===

class RedactRequest(BaseModel):
    text: str
    sensitivity: str = "medium"
    reversible: bool = False

@router.post("/pii/redact")
async def redact_pii(request: RedactRequest):
    """Redact PII from text."""
    try:
        sensitivity = SensitivityLevel(request.sensitivity)
        redactor = get_pii_redactor(sensitivity=sensitivity)
        
        redacted_text, detected = redactor.redact(
            text=request.text,
            reversible=request.reversible
        )
        
        return {
            "redacted_text": redacted_text,
            "detected_pii": detected
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pii/detect")
async def detect_pii(request: RedactRequest):
    """Detect PII without redacting."""
    try:
        sensitivity = SensitivityLevel(request.sensitivity)
        redactor = get_pii_redactor(sensitivity=sensitivity)
        
        detected = redactor.detect_only(request.text)
        
        return {"detected_pii": detected}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
