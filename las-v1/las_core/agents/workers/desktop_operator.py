from services.tool_service import get_tool_service
from services.llm_service import get_llm_service
from langchain_core.messages import HumanMessage
import re

class DesktopOperatorAgent:
    def __init__(self):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()
        self.tool_service = get_tool_service()

    def run(self, state):
        messages = state["messages"]
        last_message = messages[-1].content

        # Simple command parsing for demonstration purposes
        # In a real scenario, this would use more robust parsing or function calling
        
        move_match = re.search(r"mouse_move\((\d+),\s*(\d+)\)", last_message)
        if move_match:
            x, y = map(int, move_match.groups())
            result = self.tool_service.execute_command("mouse_move", x=x, y=y)
            return {"messages": [HumanMessage(content=result)]}

        type_match = re.search(r"keyboard_type\((.*?)\)", last_message)
        if type_match:
            text = type_match.group(1)
            result = self.tool_service.execute_command("keyboard_type", text=text)
            return {"messages": [HumanMessage(content=result)]}
            
        click_match = re.search(r"mouse_click\((\d+),\s*(\d+)\)", last_message)
        if click_match:
            x, y = map(int, click_match.groups())
            result = self.tool_service.execute_command("mouse_click", x=x, y=y)
            return {"messages": [HumanMessage(content=result)]}

        screenshot_match = re.search(r"take_screenshot\((.*?)\)", last_message)
        if screenshot_match:
            filename = screenshot_match.group(1)
            result = self.tool_service.execute_command("take_screenshot", filename=filename)
            return {"messages": [HumanMessage(content=result)]}

        return {"messages": [HumanMessage(content="I'm not sure what to do on the desktop. Please provide a command like 'mouse_move(100, 200)' or 'keyboard_type(hello)'.")]}

def desktop_operator_node(state):
    agent = DesktopOperatorAgent()
    return agent.run(state)
