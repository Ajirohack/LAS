from .memory.skill_manager import SkillManager
from .memory.reflection_manager import ReflectionManager
from .memory.schema import Skill, Reflection
from datetime import datetime

# Initialize managers
skill_manager = SkillManager()
reflection_manager = ReflectionManager()

def memory_hook_node(state):
    """
    Post-execution hook to handle skill learning and reflection.
    Called after task completion to analyze outcome.
    """
    task_success = state.get("task_success", False)
    reflection_enabled = state.get("reflection_enabled", False)
    skill_learning_enabled = state.get("skill_learning_enabled", False)
    
    result = {}
    
    # Handle successful tasks - save as skill
    if task_success and skill_learning_enabled:
        try:
            task_desc = state.get("task", "Unknown task")
            messages = state.get("messages", [])
            
            # Extract workflow from messages/state
            workflow_steps = []
            for msg in messages:
                if hasattr(msg, 'content'):
                    workflow_steps.append({
                        "role": getattr(msg, 'type', 'unknown'),
                        "content": msg.content[:200]  # Truncate for storage
                    })
            
            skill = Skill(
                name=f"skill_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=task_desc,
                workflow_steps=workflow_steps,
                success_conditions=["Task completed successfully"],
                metadata={
                    "plan": state.get("plan", ""),
                    "provider": state.get("next", "unknown")
                }
            )
            
            if skill_manager.save_skill(skill):
                result["skill_saved"] = skill.name
                print(f"✓ Skill saved: {skill.name}")
        except Exception as e:
            print(f"Failed to save skill: {e}")
    
    # Handle failed tasks - create reflection
    if not task_success and reflection_enabled:
        try:
            task_desc = state.get("task", "Unknown task")
            error_msg = state.get("feedback", "No error message")
            
            # Use LLM to analyze failure
            reflection = reflection_manager.analyze_failure(task_desc, error_msg)
            
            if reflection_manager.save_reflection(reflection):
                result["reflection_saved"] = True
                print(f"✓ Reflection saved for: {task_desc[:50]}")
                print(f"  Lessons: {reflection.lessons_learned}")
        except Exception as e:
            print(f"Failed to create reflection: {e}")
    
    return result
