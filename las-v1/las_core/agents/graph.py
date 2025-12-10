from langgraph.graph import StateGraph, END
from .state import GraphState
from .supervisor import get_supervisor_chain
from .workers.planner import planner_node
from .workers.web_surfer import web_surfer_node
from .workers.coder import coder_node

# Define the graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("Supervisor", get_supervisor_chain())
workflow.add_node("Planner", planner_node)
workflow.add_node("WebSurfer", web_surfer_node)
workflow.add_node("Coder", coder_node)

# Define edges
members = ["Planner", "WebSurfer", "Coder"]
for member in members:
    # After a worker finishes, go back to supervisor
    workflow.add_edge(member, "Supervisor")

# The supervisor decides the "next" node
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)

# Set entry point
workflow.set_entry_point("Supervisor")

# Compile the graph
graph = workflow.compile()
