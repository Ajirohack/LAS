import json
import os
from pathlib import Path
from typing import List, Optional
from .schema import Skill

class SkillManager:
    """Manages learned workflow patterns."""
    
    def __init__(self, storage_dir: str = "data/skills"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_skill(self, skill: Skill) -> bool:
        """Persist a skill to disk."""
        try:
            file_path = self.storage_dir / f"{skill.name}.json"
            with open(file_path, 'w') as f:
                json.dump(skill.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to save skill '{skill.name}': {e}")
            return False
    
    def load_skill(self, skill_name: str) -> Optional[Skill]:
        """Load a skill from disk."""
        try:
            file_path = self.storage_dir / f"{skill_name}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            return Skill(**data)
        except Exception as e:
            print(f"Failed to load skill '{skill_name}': {e}")
            return None
    
    def list_skills(self) -> List[str]:
        """List all available skill names."""
        try:
            return [f.stem for f in self.storage_dir.glob("*.json")]
        except Exception as e:
            print(f"Failed to list skills: {e}")
            return []
    
    def increment_usage(self, skill_name: str) -> bool:
        """Increment usage counter for a skill."""
        skill = self.load_skill(skill_name)
        if skill:
            skill.usage_count += 1
            return self.save_skill(skill)
        return False
    
    def delete_skill(self, skill_name: str) -> bool:
        """Delete a skill from storage."""
        try:
            file_path = self.storage_dir / f"{skill_name}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Failed to delete skill '{skill_name}': {e}")
            return False
