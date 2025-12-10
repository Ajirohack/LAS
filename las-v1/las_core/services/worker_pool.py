"""
Worker Pool Management - Manage distributed workers for scaling.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import requests

class WorkerStatus(str, Enum):
    """Worker status."""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

class Worker:
    """Represents a worker node."""
    
    def __init__(self, id: str, url: str, capabilities: List[str]):
        self.id = id
        self.url = url
        self.capabilities = capabilities
        self.status = WorkerStatus.IDLE
        self.current_task = None
        self.last_heartbeat = datetime.now()
        self.tasks_completed = 0
        self.tasks_failed = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {
            "id": self.id,
            "url": self.url,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "current_task": self.current_task,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed
        }

class WorkerPool:
    """Manages a pool of distributed workers."""
    
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
    
    def register_worker(self, worker_id: str, url: str,
                       capabilities: List[str]) -> bool:
        """Register a new worker."""
        if worker_id in self.workers:
            print(f"Worker {worker_id} already registered")
            return False
        
        worker = Worker(worker_id, url, capabilities)
        self.workers[worker_id] = worker
        print(f"✓ Worker {worker_id} registered with capabilities: {capabilities}")
        return True
    
    def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker."""
        if worker_id in self.workers:
            del self.workers[worker_id]
            print(f"✓ Worker {worker_id} unregistered")
            return True
        return False
    
    def get_worker(self, worker_id: str) -> Optional[Worker]:
        """Get worker by ID."""
        return self.workers.get(worker_id)
    
    def list_workers(self, status: Optional[WorkerStatus] = None) -> List[Worker]:
        """List workers, optionally filtered by status."""
        workers = list(self.workers.values())
        
        if status:
            workers = [w for w in workers if w.status == status]
        
        return workers
    
    def find_available_worker(self, capability: Optional[str] = None) -> Optional[Worker]:
        """Find an available worker with optional capability filter."""
        for worker in self.workers.values():
            if worker.status != WorkerStatus.IDLE:
                continue
            
            if capability and capability not in worker.capabilities:
                continue
            
            return worker
        
        return None
    
    def assign_task(self, worker_id: str, task_id: str) -> bool:
        """Assign a task to a worker."""
        worker = self.workers.get(worker_id)
        if not worker:
            return False
        
        if worker.status != WorkerStatus.IDLE:
            print(f"Worker {worker_id} is not idle")
            return False
        
        worker.status = WorkerStatus.BUSY
        worker.current_task = task_id
        return True
    
    def complete_task(self, worker_id: str, success: bool = True):
        """Mark task as complete for a worker."""
        worker = self.workers.get(worker_id)
        if not worker:
            return
        
        worker.status = WorkerStatus.IDLE
        worker.current_task = None
        
        if success:
            worker.tasks_completed += 1
        else:
            worker.tasks_failed += 1
    
    def heartbeat(self, worker_id: str) -> bool:
        """Update worker heartbeat."""
        worker = self.workers.get(worker_id)
        if not worker:
            return False
        
        worker.last_heartbeat = datetime.now()
        return True
    
    def health_check(self, worker_id: str) -> bool:
        """Check if worker is healthy."""
        worker = self.workers.get(worker_id)
        if not worker:
            return False
        
        try:
            response = requests.get(f"{worker.url}/health", timeout=2)
            return response.status_code == 200
        except:
            worker.status = WorkerStatus.OFFLINE
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        total = len(self.workers)
        idle = len([w for w in self.workers.values() if w.status == WorkerStatus.IDLE])
        busy = len([w for w in self.workers.values() if w.status == WorkerStatus.BUSY])
        offline = len([w for w in self.workers.values() if w.status == WorkerStatus.OFFLINE])
        
        total_completed = sum(w.tasks_completed for w in self.workers.values())
        total_failed = sum(w.tasks_failed for w in self.workers.values())
        
        return {
            "total_workers": total,
            "idle": idle,
            "busy": busy,
            "offline": offline,
            "total_tasks_completed": total_completed,
            "total_tasks_failed": total_failed,
            "utilization": round((busy / total * 100) if total > 0 else 0, 2)
        }

# Create singleton instance
_worker_pool: Optional[WorkerPool] = None

def get_worker_pool() -> WorkerPool:
    """Get or create WorkerPool instance."""
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = WorkerPool()
    return _worker_pool
