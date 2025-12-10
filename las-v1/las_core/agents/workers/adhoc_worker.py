from langchain_core.messages import HumanMessage, SystemMessage
from services.llm_service import get_llm_service

class AdHocWorker:
    def __init__(self):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()

    def run(self, state):
        messages = state["messages"]
        role = state.get("worker_role", "Assistant")
        instructions = state.get("worker_instructions", "You are a helpful assistant.")
        
        system_prompt = (
            f"You are {role}. {instructions}\n"
            "Perform the task requested by the user."
        )
        
        # Create a new chain with the dynamic system prompt
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({"messages": messages})
        return {"messages": [response]}

def adhoc_worker_node(state):
    agent = AdHocWorker()
    result = agent.run(state)
    return result
