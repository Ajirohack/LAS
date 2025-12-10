from langchain_core.messages import HumanMessage, SystemMessage
from services.llm_service import get_llm_service
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

class CriticAgent:
    def __init__(self):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()

    def run(self, state):
        messages = state["messages"]
        plan = state.get("plan", "")
        
        system_prompt = (
            "You are a critical reviewer. Your job is to evaluate the proposed plan."
            " Check for feasibility, safety, and completeness."
            " If the plan is good, respond with 'APPROVE'."
            " If the plan is flawed, respond with 'REJECT' and provide constructive feedback."
            " Return your response in JSON format with keys: 'status' (APPROVE/REJECT) and 'feedback' (string)."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"Here is the plan to review:\n{plan}\n\nEvaluate it.")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            response = chain.invoke({})
            return {
                "critique": response.get("status", "REJECT"),
                "feedback": response.get("feedback", "Failed to parse critique.")
            }
        except Exception as e:
            return {
                "critique": "REJECT",
                "feedback": f"Error during critique: {str(e)}"
            }

def critic_node(state):
    agent = CriticAgent()
    result = agent.run(state)
    return result
