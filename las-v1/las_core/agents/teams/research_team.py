from langgraph.graph import StateGraph, END
from ..state import GraphState
from ..supervisor import get_supervisor_chain
from ..workers.web_surfer import web_surfer_node
from ..workers.document_analyst import document_analyst_node

def create_research_graph():
    members = ["WebSurfer", "DocumentAnalyst"]
    supervisor_chain = get_supervisor_chain(members)

    workflow = StateGraph(GraphState)
    
    workflow.add_node("ResearchSupervisor", supervisor_chain)
    workflow.add_node("WebSurfer", web_surfer_node)
    workflow.add_node("DocumentAnalyst", document_analyst_node)

    for member in members:
        workflow.add_edge(member, "ResearchSupervisor")

    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    
    workflow.add_conditional_edges("ResearchSupervisor", lambda x: x["next"], conditional_map)
    workflow.set_entry_point("ResearchSupervisor")
    
    return workflow.compile()
