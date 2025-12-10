from langchain_core.messages import HumanMessage
from services.llm_service import get_llm_service

def document_analyst_node(state):
    messages = state["messages"]
    llm_service = get_llm_service()
    llm = llm_service.get_langchain_llm()
    
    # Simple implementation: The analyst just processes the last message
    # In a real implementation, this would use RAG or file reading tools
    response = llm.invoke(messages)
    
    return {
        "messages": [
            HumanMessage(content=response.content, name="DocumentAnalyst")
        ]
    }
