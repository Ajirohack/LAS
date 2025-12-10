import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from .schema import Reflection
from services.llm_service import get_llm_service

class ReflectionManager:
    """Manages post-mortem analysis of failures."""
    
    def __init__(self, storage_dir: str = "data/reflections"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.llm_service = get_llm_service()
    
    def analyze_failure(self, task_description: str, error_message: str) -> Reflection:
        """Use LLM to analyze a failure and extract lessons."""
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at analyzing task failures and extracting actionable lessons."),
            ("human", f"Task: {task_description}\n\nError: {error_message}\n\nAnalyze this failure and provide:\n1. A clear explanation of why it failed\n2. Specific lessons learned\n3. How to avoid this in the future\n\nProvide your response as JSON with keys: failure_reason, lessons_learned (list)")
        ])
        
        try:
            llm = self.llm_service.get_langchain_llm()
            from langchain_core.output_parsers import JsonOutputParser
            chain = prompt | llm | JsonOutputParser()
            
            result = chain.invoke({})
            
            return Reflection(
                task_description=task_description,
                failure_reason=result.get("failure_reason", error_message),
                lessons_learned=result.get("lessons_learned", []),
                metadata={"original_error": error_message}
            )
        except Exception as e:
            # Fallback if LLM analysis fails
            return Reflection(
                task_description=task_description,
                failure_reason=error_message,
                lessons_learned=["Failed to analyze with LLM"],
                metadata={"analysis_error": str(e)}
            )
    
    def save_reflection(self, reflection: Reflection) -> bool:
        """Persist a reflection to disk."""
        try:
            timestamp = reflection.created_at.strftime("%Y%m%d_%H%M%S")
            safe_task = "".join(c for c in reflection.task_description[:50] if c.isalnum() or c in (' ', '_')).strip()
            filename = f"{timestamp}_{safe_task}.json"
            
            file_path = self.storage_dir / filename
            with open(file_path, 'w') as f:
                json.dump(reflection.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to save reflection: {e}")
            return False
    
    def query_reflections(self, task_type: Optional[str] = None, limit: int = 10) -> List[Reflection]:
        """Retrieve reflections, optionally filtered by task type."""
        try:
            reflections = []
            for file_path in sorted(self.storage_dir.glob("*.json"), reverse=True)[:limit * 2]:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    reflection = Reflection(**data)
                    
                    if task_type is None or task_type.lower() in reflection.task_description.lower():
                        reflections.append(reflection)
                        
                    if len(reflections) >= limit:
                        break
            
            return reflections
        except Exception as e:
            print(f"Failed to query reflections: {e}")
            return []
    
    def get_lessons_for_task(self, task_description: str, limit: int = 5) -> List[str]:
        """Get relevant lessons learned for a similar task."""
        reflections = self.query_reflections(task_type=task_description, limit=limit)
        lessons = []
        for reflection in reflections:
            lessons.extend(reflection.lessons_learned)
        return lessons[:limit]
