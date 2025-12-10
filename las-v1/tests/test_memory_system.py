import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../las_core")))

try:
    from agents.hierarchical_graph import graph
    from agents.memory.skill_manager import SkillManager
    from agents.memory.reflection_manager import ReflectionManager
    from agents.memory.schema import Skill, Reflection
    from datetime import datetime
    
    print("=== Long-Term Memory System Verification ===\n")
    
    # 1. Verify graph compilation
    print("1. Graph Compilation:")
    nodes = graph.nodes.keys()
    print(f"   Nodes: {list(nodes)}")
    
    if "MemoryHook" in nodes:
        print("   ✓ MemoryHook found in graph")
    else:
        print("   ✗ MemoryHook NOT found in graph")
        sys.exit(1)
    
    # 2. Test SkillManager
    print("\n2. SkillManager:")
    skill_mgr = SkillManager(storage_dir="data/test_skills")
    
    test_skill = Skill(
        name="test_coding_workflow",
        description="Example coding workflow",
        workflow_steps=[
            {"role": "planner", "content": "Analyzed requirements"},
            {"role": "coder", "content": "Implemented solution"}
        ],
        success_conditions=["Code runs successfully"],
        metadata={"language": "python"}
    )
    
    if skill_mgr.save_skill(test_skill):
        print("   ✓ Skill saved successfully")
    else:
        print("   ✗ Failed to save skill")
        sys.exit(1)
    
    loaded_skill = skill_mgr.load_skill("test_coding_workflow")
    if loaded_skill and loaded_skill.name == test_skill.name:
        print(f"   ✓ Skill loaded successfully: {loaded_skill.name}")
    else:
        print("   ✗ Failed to load skill")
        sys.exit(1)
    
    skills = skill_mgr.list_skills()
    print(f"   ✓ Skills in storage: {skills}")
    
    # 3. Test ReflectionManager
    print("\n3. ReflectionManager:")
    reflection_mgr = ReflectionManager(storage_dir="data/test_reflections")
    
    test_reflection = Reflection(
        task_description="Build a web scraper",
        failure_reason="Timeout error",
        lessons_learned=["Add retry logic", "Increase timeout"],
        metadata={"error_code": 408}
    )
    
    if reflection_mgr.save_reflection(test_reflection):
        print("   ✓ Reflection saved successfully")
    else:
        print("   ✗ Failed to save reflection")
        sys.exit(1)
    
    reflections = reflection_mgr.query_reflections(limit=5)
    print(f"   ✓ Reflections in storage: {len(reflections)}")
    
    lessons = reflection_mgr.get_lessons_for_task("web scraper", limit=3)
    print(f"   ✓ Relevant lessons: {lessons}")
    
    print("\n=== All Verifications Passed ===")
    
except Exception as e:
    print(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
