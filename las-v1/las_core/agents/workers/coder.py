from langchain_core.messages import HumanMessage
from services.llm_service import get_llm_service
from config.settings import settings

class CoderAgent:
    def __init__(self):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()

    def run(self, state):
        messages = state["messages"]
        plan = state.get("plan", "")
        
        prompt = f"You are a coding expert. Implement the following task: {messages[-1].content}. "
        if plan:
            prompt += f"Follow this plan: {plan}"
            
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"messages": [response]}

def coder_node(state):
    agent = CoderAgent()
    result = agent.run(state)
    return result
