from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from services.llm_service import get_llm_service
from config.settings import settings
from .state import GraphState

class SupervisorAgent:
    def __init__(self, members: list, system_prompt: str):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()
        
        options = ["FINISH"] + members
        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": options},
                        ],
                    },
                    "worker_role": {
                        "title": "Worker Role",
                        "type": "string",
                        "description": "The specific role for the AdHocWorker (e.g., 'Python Expert', 'Poet'). Only used if next is 'AdHocWorker'."
                    },
                    "worker_instructions": {
                        "title": "Worker Instructions",
                        "type": "string",
                        "description": "Specific instructions for the AdHocWorker. Only used if next is 'AdHocWorker'."
                    }
                },
                "required": ["next"],
            },
        }

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}."
                    " Respond with a JSON object containing a single key 'next' and the selected option as the value."
                    " Example: {{'next': 'Planner'}}"
                ),
            ]
        ).partial(options=str(options), members=", ".join(members))

        if hasattr(self.llm, "bind_functions"):
            self.chain = (
                prompt
                | self.llm.bind_functions(functions=[function_def], function_call="route")
                | JsonOutputFunctionsParser()
            )
        else:
            from langchain_core.output_parsers import JsonOutputParser
            self.chain = (
                prompt
                | self.llm
                | JsonOutputParser()
            )

    def run(self, state: GraphState):
        return self.chain.invoke(state)

def get_supervisor_chain(members=None):
    if members is None:
        members = ["Planner", "WebSurfer", "Coder"]
    
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )
    return SupervisorAgent(members, system_prompt).chain
