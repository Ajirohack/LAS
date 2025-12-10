from langchain_core.messages import HumanMessage
from services.tool_service import get_tool_service
from config.settings import settings

from langchain.tools import Tool

from services.llm_service import get_llm_service


class WebSurferAgent:
    def __init__(self):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()
        self.tool_service = get_tool_service()

    async def run(self, state):
        messages = state["messages"]
        # Logic to decide if to search or browse
        # For simplicity, we'll just assume the last message contains the instruction
        last_message = messages[-1].content

        if "search" in last_message.lower():
            # Use search tool
            # In a real implementation, we'd use function calling to extract query
            result = await self.tool_service.execute_command(
                "web_search", query=last_message, num_results=3
            )
            return {"messages": [HumanMessage(content=f"Search Results: {result}")]}
        elif "browse" in last_message.lower() or "http" in last_message:
            # Use browse tool
            # Extract URL (simplified)
            import re

            url = re.search(r"(https?://\S+)", last_message)
            if url:
                result = await self.tool_service.execute_command(
                    "browse_website", url=url.group(0)
                )
                return {
                    "messages": [
                        HumanMessage(content=f"Page Content: {result[:1000]}...")
                    ]
                }

        return {
            "messages": [
                HumanMessage(
                    content="I'm not sure what to browse. Please provide a URL or search query."
                )
            ]
        }


async def web_surfer_node(state):
    agent = WebSurferAgent()
    return await agent.run(state)
