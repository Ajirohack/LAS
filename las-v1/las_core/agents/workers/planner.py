from langchain_core.messages import HumanMessage
from services.llm_service import get_llm_service
from config.settings import settings
from langchain_community.chat_models import ChatOllama

class PlannerAgent:
    def __init__(self):
        self.llm = ChatOllama(model=settings.provider_model, base_url=settings.provider_server_address)

    def run(self, state):
        messages = state["messages"]
        # Logic to generate a plan based on the request
        response = self.llm.invoke(messages + [HumanMessage(content="Create a step-by-step plan for this task.")])
        return {"messages": [response], "plan": response.content}

def planner_node(state):
    agent = PlannerAgent()
    result = agent.run(state)
    return result
