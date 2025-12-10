from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Skill(BaseModel):
    """Represents a learned workflow pattern."""
    name: str
    description: str
    workflow_steps: List[Dict[str, Any]]
    success_conditions: List[str]
    metadata: Dict[str, Any]
    created_at: datetime = datetime.now()
    usage_count: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Reflection(BaseModel):
    """Represents a post-mortem analysis of a failure."""
    task_description: str
    failure_reason: str
    lessons_learned: List[str]
    similar_tasks: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
