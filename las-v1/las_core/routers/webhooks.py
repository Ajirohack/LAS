from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from webhooks.webhook_manager import get_webhook_manager

router = APIRouter()

class WebhookRegistration(BaseModel):
    event: str
    url: str
    secret: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

@router.post("/register")
async def register_webhook(registration: WebhookRegistration):
    """Register a webhook for an event."""
    try:
        manager = get_webhook_manager()
        webhook_id = manager.register(
            event=registration.event,
            url=registration.url,
            secret=registration.secret,
            headers=registration.headers
        )
        return {"webhook_id": webhook_id, "status": "registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.delete("/{webhook_id}")
async def unregister_webhook(webhook_id: str):
    """Unregister a webhook."""
    try:
        manager = get_webhook_manager()
        success = manager.unregister(webhook_id)
        if success:
            return {"status": "unregistered"}
        else:
            raise HTTPException(status_code=404, detail="Webhook not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_webhooks(event: Optional[str] = None):
    """List registered webhooks."""
    try:
        manager = get_webhook_manager()
        webhooks = manager.list_webhooks(event=event)
        return {"webhooks": webhooks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def list_events():
    """List available webhook events."""
    return {
        "events": [
            {
                "name": "task_complete",
                "description": "Triggered when a task is completed"
            },
            {
                "name": "skill_learned",
                "description": "Triggered when a new skill is learned"
            },
            {
                "name": "reflection_created",
                "description": "Triggered when a reflection is created"
            }
        ]
    }
