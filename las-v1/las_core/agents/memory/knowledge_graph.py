from typing import Dict, List, Any
from pathlib import Path
import json
from .skill_manager import SkillManager
from .reflection_manager import ReflectionManager

class KnowledgeGraph:
    """Generates graph data from skills and reflections for visualization."""
    
    def __init__(self):
        self.skill_manager = SkillManager()
        self.reflection_manager = ReflectionManager()
    
    def generate_graph(self) -> Dict[str, Any]:
        """
        Generate a graph structure with nodes and edges.
        
        Returns:
            Dict with 'nodes' and 'edges' lists for visualization libraries.
        """
        nodes = []
        edges = []
        node_id_counter = 0
        
        # Create node ID mapping
        node_map = {}
        
        # Add skill nodes
        skills = self.skill_manager.list_skills()
        for skill_name in skills:
            skill = self.skill_manager.load_skill(skill_name)
            if skill:
                node_id = f"skill_{node_id_counter}"
                node_id_counter += 1
                
                nodes.append({
                    "id": node_id,
                    "label": skill.name,
                    "type": "skill",
                    "description": skill.description,
                    "usage_count": skill.usage_count,
                    "metadata": skill.metadata
                })
                node_map[skill.name] = node_id
                
                # Create edges to related tasks (from workflow steps)
                for step in skill.workflow_steps:
                    task_label = step.get("content", "")[:50]
                    if task_label:
                        task_node_id = f"task_{node_id_counter}"
                        node_id_counter += 1
                        
                        # Add task node if not exists
                        if task_node_id not in [n["id"] for n in nodes]:
                            nodes.append({
                                "id": task_node_id,
                                "label": task_label,
                                "type": "task",
                                "role": step.get("role", "unknown")
                            })
                        
                        # Add edge from skill to task
                        edges.append({
                            "from": node_id,
                            "to": task_node_id,
                            "label": "contains"
                        })
        
        # Add reflection nodes
        reflections = self.reflection_manager.query_reflections(limit=20)
        for reflection in reflections:
            node_id = f"reflection_{node_id_counter}"
            node_id_counter += 1
            
            nodes.append({
                "id": node_id,
                "label": reflection.task_description[:50],
                "type": "reflection",
                "failure_reason": reflection.failure_reason,
                "lessons": reflection.lessons_learned
            })
            
            # Create edges to similar tasks
            for similar_task in reflection.similar_tasks:
                # Find or create task node
                matching_nodes = [n for n in nodes if n.get("label") == similar_task[:50] and n.get("type") == "task"]
                if matching_nodes:
                    task_node_id = matching_nodes[0]["id"]
                else:
                    task_node_id = f"task_{node_id_counter}"
                    node_id_counter += 1
                    nodes.append({
                        "id": task_node_id,
                        "label": similar_task[:50],
                        "type": "task"
                    })
                
                edges.append({
                    "from": node_id,
                    "to": task_node_id,
                    "label": "related_to"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_skills": len(skills),
                "total_reflections": len(reflections),
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }
    
    def export_to_json(self, output_path: str = "data/knowledge_graph.json") -> bool:
        """Export graph to JSON file."""
        try:
            graph_data = self.generate_graph()
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(graph_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to export graph: {e}")
            return False
