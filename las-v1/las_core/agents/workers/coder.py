from langchain_core.messages import HumanMessage
from config.settings import settings
from langchain_community.chat_models import ChatOllama

class CoderAgent:
    def __init__(self):
        self.llm = ChatOllama(model=settings.provider_model, base_url=settings.provider_server_address)

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
