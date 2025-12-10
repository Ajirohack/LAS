"""
Webhook System - Event-driven integrations for LAS
"""

import json
import requests
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import threading
import time

class WebhookManager:
    """Manages webhook registrations and delivery."""
    
    def __init__(self, storage_dir: str = "data/webhooks"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.webhooks: Dict[str, List[Dict[str, Any]]] = {}
        self.load_webhooks()
    
    def load_webhooks(self):
        """Load webhooks from storage."""
        webhook_file = self.storage_dir / "webhooks.json"
        if webhook_file.exists():
            try:
                with open(webhook_file, 'r') as f:
                    self.webhooks = json.load(f)
            except Exception as e:
                print(f"Failed to load webhooks: {e}")
                self.webhooks = {}
    
    def save_webhooks(self):
        """Save webhooks to storage."""
        webhook_file = self.storage_dir / "webhooks.json"
        try:
            with open(webhook_file, 'w') as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            print(f"Failed to save webhooks: {e}")
    
    def register(self, event: str, url: str, secret: Optional[str] = None,
                headers: Optional[Dict[str, str]] = None) -> str:
        """
        Register a webhook for an event.
        
        Args:
            event: Event name (task_complete, skill_learned, etc.)
            url: Webhook URL
            secret: Optional secret for HMAC signing
            headers: Optional custom headers
        
        Returns:
            Webhook ID
        """
        webhook_id = f"{event}_{int(time.time())}"
        
        webhook = {
            "id": webhook_id,
            "event": event,
            "url": url,
            "secret": secret,
            "headers": headers or {},
            "created_at": datetime.now().isoformat(),
            "enabled": True
        }
        
        if event not in self.webhooks:
            self.webhooks[event] = []
        
        self.webhooks[event].append(webhook)
        self.save_webhooks()
        
        return webhook_id
    
    def unregister(self, webhook_id: str) -> bool:
        """Unregister a webhook."""
        for event, hooks in self.webhooks.items():
            self.webhooks[event] = [h for h in hooks if h["id"] != webhook_id]
        
        self.save_webhooks()
        return True
    
    def list_webhooks(self, event: Optional[str] = None) -> List[Dict[str, Any]]:
        """List registered webhooks."""
        if event:
            return self.webhooks.get(event, [])
        
        # Return all webhooks
        all_webhooks = []
        for hooks in self.webhooks.values():
            all_webhooks.extend(hooks)
        return all_webhooks
    
    def trigger(self, event: str, payload: Dict[str, Any]):
        """
        Trigger webhooks for an event.
        
        Args:
            event: Event name
            payload: Event payload
        """
        hooks = self.webhooks.get(event, [])
        
        for webhook in hooks:
            if not webhook.get("enabled"):
                continue
            
            # Deliver asynchronously
            thread = threading.Thread(
                target=self._deliver_webhook,
                args=(webhook, payload)
            )
            thread.daemon = True
            thread.start()
    
    def _deliver_webhook(self, webhook: Dict[str, Any], payload: Dict[str, Any],
                        max_retries: int = 3):
        """Deliver a webhook with retry logic."""
        url = webhook["url"]
        headers = webhook.get("headers", {})
        headers["Content-Type"] = "application/json"
        
        # Add signature if secret provided
        secret = webhook.get("secret")
        if secret:
            import hmac
            import hashlib
            
            payload_bytes = json.dumps(payload).encode()
            signature = hmac.new(
                secret.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = signature
        
        # Retry logic
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code < 300:
                    print(f"✓ Webhook delivered to {url}")
                    return
                else:
                    print(f"Webhook failed: {response.status_code}")
            
            except Exception as e:
                print(f"Webhook delivery error (attempt {attempt+1}): {e}")
            
            # Exponential backoff
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        print(f"✗ Webhook delivery failed after {max_retries} attempts")

# Create singleton instance
_webhook_manager: Optional[WebhookManager] = None

def get_webhook_manager() -> WebhookManager:
    """Get or create WebhookManager instance."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager

# Event trigger helpers
def trigger_task_complete(task: str, result: Any):
    """Trigger task_complete event."""
    manager = get_webhook_manager()
    manager.trigger("task_complete", {
        "event": "task_complete",
        "task": task,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

def trigger_skill_learned(skill_name: str):
    """Trigger skill_learned event."""
    manager = get_webhook_manager()
    manager.trigger("skill_learned", {
        "event": "skill_learned",
        "skill": skill_name,
        "timestamp": datetime.now().isoformat()
    })

def trigger_reflection_created(task: str, lessons: List[str]):
    """Trigger reflection_created event."""
    manager = get_webhook_manager()
    manager.trigger("reflection_created", {
        "event": "reflection_created",
        "task": task,
        "lessons": lessons,
        "timestamp": datetime.now().isoformat()
    })
