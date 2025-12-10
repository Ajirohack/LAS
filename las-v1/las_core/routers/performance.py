from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from services.semantic_cache import get_semantic_cache
from services.cost_tracker import get_cost_tracker
from services.task_queue import get_task_queue, TaskPriority, TaskStatus
from services.worker_pool import get_worker_pool
from middleware.auth_middleware import require_auth, require_admin_auth

router = APIRouter()

# === Semantic Cache Endpoints ===

@router.get("/cache/stats")
async def get_cache_stats():
    """Get semantic cache statistics."""
    try:
        cache = get_semantic_cache()
        return cache.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/invalidate")
async def invalidate_cache(query: Optional[str] = None):
    """Invalidate cache entries."""
    try:
        cache = get_semantic_cache()
        cache.invalidate(query)
        return {"status": "invalidated", "query": query or "all"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear-stats")
async def clear_cache_stats(current_user = Depends(require_admin_auth)):
    """Clear cache statistics (admin only)."""
    try:
        cache = get_semantic_cache()
        cache.clear_stats()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Cost Tracking Endpoints ===

class BudgetRequest(BaseModel):
    agent: str
    amount: float

@router.get("/cost/summary")
async def get_cost_summary(period: str = "daily"):
    """Get cost summary for a period (daily, monthly, total)."""
    try:
        tracker = get_cost_tracker()
        return tracker.get_cost_summary(period=period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cost/budget")
async def set_budget(request: BudgetRequest):
    """Set budget limit for an agent."""
    try:
        tracker = get_cost_tracker()
        tracker.set_budget(request.agent, request.amount)
        return {"agent": request.agent, "budget": request.amount}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cost/budget/{agent}")
async def get_budget(agent: str):
    """Get budget limit for an agent."""
    try:
        tracker = get_cost_tracker()
        budget = tracker.get_budget(agent)
        if budget is None:
            raise HTTPException(status_code=404, detail=f"No budget set for agent '{agent}'")
        return {"agent": agent, "budget": budget}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Task Queue Endpoints ===

class TaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]
    priority: str = "normal"
    agent: Optional[str] = None

@router.post("/queue/enqueue")
async def enqueue_task(request: TaskRequest):
    """Enqueue a task for async processing."""
    try:
        queue = get_task_queue()
        priority = TaskPriority(request.priority)
        task_id = queue.enqueue(
            task_type=request.task_type,
            payload=request.payload,
            priority=priority,
            agent=request.agent
        )
        return {"task_id": task_id, "status": "enqueued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status."""
    try:
        queue = get_task_queue()
        task = queue.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/stats")
async def get_queue_stats():
    """Get queue statistics."""
    try:
        queue = get_task_queue()
        return queue.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Worker Pool Endpoints ===

class WorkerRegistration(BaseModel):
    worker_id: str
    url: str
    capabilities: List[str]

@router.post("/workers/register")
async def register_worker(request: WorkerRegistration):
    """Register a worker."""
    try:
        pool = get_worker_pool()
        success = pool.register_worker(
            worker_id=request.worker_id,
            url=request.url,
            capabilities=request.capabilities
        )
        if success:
            return {"status": "registered", "worker_id": request.worker_id}
        else:
            raise HTTPException(status_code=400, detail="Worker already registered")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workers")
async def list_workers():
    """List all workers."""
    try:
        pool = get_worker_pool()
        workers = pool.list_workers()
        return {"workers": [w.to_dict() for w in workers]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workers/stats")
async def get_worker_stats():
    """Get worker pool statistics."""
    try:
        pool = get_worker_pool()
        return pool.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
