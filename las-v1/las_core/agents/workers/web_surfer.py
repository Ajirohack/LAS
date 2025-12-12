from langchain_core.messages import HumanMessage
from services.tool_service import get_tool_service
from services.vision_service import get_vision_service
from config.settings import settings
import re
import os

from services.llm_service import get_llm_service


class WebSurferAgent:
    def __init__(self):
        self.llm_service = get_llm_service()
        self.llm = self.llm_service.get_langchain_llm()
        self.tool_service = get_tool_service()
        self.vision_service = get_vision_service()

    async def run(self, state):
        messages = state["messages"]
        last_message = messages[-1].content
        last_message_lower = last_message.lower()

        if "search" in last_message_lower:
            # Use search tool
            result = await self.tool_service.execute_command(
                "web_search", query=last_message, num_results=3
            )
            return {"messages": [HumanMessage(content=f"Search Results: {result}")]}
        
        elif "browse" in last_message_lower or "http" in last_message:
            # Use browse tool
            url_match = re.search(r"(https?://\S+)", last_message)
            if url_match:
                url = url_match.group(0)
                # If "look" or "see" is mentioned, use vision
                if "look" in last_message_lower or "see" in last_message_lower or "screenshot" in last_message_lower:
                    return await self.browse_and_analyze(url, last_message)
                
                # Standard text browsing
                result = await self.tool_service.execute_command(
                    "browse_website", url=url
                )
                return {
                    "messages": [
                        HumanMessage(content=f"Page Content: {result[:2000]}...") # Truncate for simplicity
                    ]
                }

        elif "look" in last_message_lower or "screenshot" in last_message_lower:
             # Capture current page if no URL is provided (assuming browser is open/stateful logic if applicable)
             # But here we assume stateless per turn or we need to know the context.
             # For now, let's assume we need a URL, or we try to screenshot the LAST visited URL if we had state.
             # Since this is a simple implementation, we'll ask for URL if missing.
             return {
                 "messages": [HumanMessage(content="Please provide the URL you want me to look at.")]
             }

        return {
            "messages": [
                HumanMessage(
                    content="I'm not sure what to browse. Please provide a URL or search instruction."
                )
            ]
        }

    async def browse_and_analyze(self, url: str, prompt: str) -> dict:
        """Browse a URL, take a screenshot, and analyze it."""
        try:
            # 1. Navigate
            await self.tool_service.execute_command("browse_website", url=url)
            
            # 2. Screenshot
            # We assume 'take_screenshot' saves to a predictable temp path or returns the path
            screenshot_path = await self.tool_service.execute_command("take_screenshot", filename="temp_vision.png")
            
            # Check if command returned path or message
            if "saved to" in str(screenshot_path):
                # Extract path or assume it's created
                # For safety, let's use a known path if possible, or parse the result.
                # If 'filename' arg was respected, it should be at 'temp_vision.png' relative to CWD or absolute.
                # Let's assume absolute path handling in extension or CWD.
                # Better: Browser extension should return absolute path.
                
                # If screenshot_path is the string message. Let's try to use the filename we passed if it exists.
                target_file = "temp_vision.png" 
                if os.path.exists(target_file):
                    analysis = self.vision_service.analyze_image(target_file, prompt=prompt)
                    return {"messages": [HumanMessage(content=f"Visual Analysis of {url}:\n{analysis}")]}
            
            return {"messages": [HumanMessage(content=f"Failed to capture screenshot: {screenshot_path}")]}
            
        except Exception as e:
            return {"messages": [HumanMessage(content=f"Error during visual browsing: {str(e)}")]}

async def web_surfer_node(state):
    agent = WebSurferAgent()
    return await agent.run(state)
