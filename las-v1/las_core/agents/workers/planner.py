from langchain_core.messages import HumanMessage
from services.llm_service import get_llm_service
from config.settings import settings

class PlannerAgent:
    def __init__(self):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()

    def run(self, state):
        messages = state["messages"]
        # Logic to generate a plan based on the request
        # We invoke synchronously if the LLM provided is sync, or .invoke handles it.
        # But get_langchain_llm returns a standard LangChain runnable.
        response = self.llm.invoke(messages + [HumanMessage(content="Create a step-by-step plan for this task.")])
        return {"messages": [response], "plan": response.content}

def planner_node(state):
    agent = PlannerAgent()
    result = agent.run(state)
    return result
