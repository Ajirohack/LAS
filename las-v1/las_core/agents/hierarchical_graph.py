from langgraph.graph import StateGraph, END
from .state import GraphState
from .supervisor import get_supervisor_chain
from .teams.research_team import create_research_graph
from .teams.coding_team import create_coding_graph
from .workers.planner import planner_node
from .workers.critic import critic_node
from .workers.adhoc_worker import adhoc_worker_node
from .memory_hooks import memory_hook_node

# Define the top-level graph
workflow = StateGraph(GraphState)

# Create subgraphs
research_graph = create_research_graph()
coding_graph = create_coding_graph()

# Add nodes
# The supervisor here decides which TEAM to call
top_members = ["ResearchTeam", "CodingTeam", "AdHocWorker"]
workflow.add_node("TopSupervisor", get_supervisor_chain(top_members))
workflow.add_node("ResearchTeam", research_graph)
workflow.add_node("CodingTeam", coding_graph)
workflow.add_node("Planner", planner_node)
workflow.add_node("Critic", critic_node)
workflow.add_node("AdHocWorker", adhoc_worker_node)
workflow.add_node("MemoryHook", memory_hook_node)

# Define edges
# Start with Planner -> Critic
workflow.add_edge("Planner", "Critic")

# Critic routing logic
def critique_routing(state):
    critique = state.get("critique")
    if critique == "APPROVE":
        return "TopSupervisor"
    else:
        return "Planner"

workflow.add_conditional_edges("Critic", critique_routing, {
    "TopSupervisor": "TopSupervisor",
    "Planner": "Planner"
})

# Supervisor edges - route to MemoryHook instead of directly back
for member in top_members:
    workflow.add_edge(member, "MemoryHook")

# Memory hook routes back to supervisor or ends
def memory_routing(state):
    # Check if supervisor wants to continue or finish
    next_action = state.get("next", "FINISH")
    if next_action == "FINISH":
        return "END"
    else:
        return "TopSupervisor"

workflow.add_conditional_edges("MemoryHook", memory_routing, {
    "TopSupervisor": "TopSupervisor",
    "END": END
})

# Conditional edges for Supervisor
conditional_map = {k: k for k in top_members}
conditional_map["FINISH"] = "MemoryHook"  # Route to memory hook before finishing
workflow.add_conditional_edges("TopSupervisor", lambda x: x["next"], conditional_map)

# Set entry point to Planner for debate mode
workflow.set_entry_point("Planner")

graph = workflow.compile()
