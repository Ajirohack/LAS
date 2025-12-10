from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from agents.memory.knowledge_graph import KnowledgeGraph
from agents.memory.skill_manager import get_skill_manager
from agents.memory.reflection_manager import get_reflection_manager
from middleware.auth_middleware import require_auth

router = APIRouter()

# Initialize managers
knowledge_graph = KnowledgeGraph()
skill_manager = get_skill_manager()
reflection_manager = get_reflection_manager()

@router.get("/knowledge-graph")
async def get_knowledge_graph():
    """Get the knowledge graph of all skills and reflections."""
    try:
        graph_data = knowledge_graph.generate_graph()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate knowledge graph: {str(e)}")

@router.get("/skills")
async def list_skills():
    """List all saved skills."""
    try:
        skills = skill_manager.list_skills()
        return {"skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list skills: {str(e)}")

@router.get("/skills/{skill_name}")
async def get_skill(skill_name: str):
    """Get details of a specific skill."""
    try:
        skill = skill_manager.load_skill(skill_name)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
        return skill.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load skill: {str(e)}")

@router.get("/reflections")
async def list_reflections(task_type: str = None, limit: int = 10):
    """List reflections, optionally filtered by task type."""
    try:
        reflections =reflection_manager.query_reflections(task_type=task_type, limit=limit)
        return {"reflections": [r.dict() for r in reflections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reflections: {str(e)}")

@router.get("/lessons/{task_description}")
async def get_lessons(task_description: str, limit: int = 5):
    """Get relevant lessons for a task."""
    try:
        lessons = reflection_manager.get_lessons_for_task(task_description, limit=limit)
        return {"lessons": lessons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lessons: {str(e)}")
