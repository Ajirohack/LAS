from langgraph.graph import StateGraph, END
from ..state import GraphState
from ..supervisor import get_supervisor_chain
from ..workers.coder import coder_node
# Assuming we might add a Reviewer later, for now just Coder

def create_coding_graph():
    members = ["Coder"]
    supervisor_chain = get_supervisor_chain(members)

    workflow = StateGraph(GraphState)
    
    workflow.add_node("CodingSupervisor", supervisor_chain)
    workflow.add_node("Coder", coder_node)

    for member in members:
        workflow.add_edge(member, "CodingSupervisor")

    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    
    workflow.add_conditional_edges("CodingSupervisor", lambda x: x["next"], conditional_map)
    workflow.set_entry_point("CodingSupervisor")
    
    return workflow.compile()
