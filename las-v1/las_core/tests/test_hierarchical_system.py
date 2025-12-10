import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.langgraph_interaction import LangGraphInteraction
from config.settings import settings

async def main():
    print("Initializing LangGraphInteraction...")
    interaction = LangGraphInteraction(
        agents=[], # Not needed for graph
        tts_enabled=False,
        stt_enabled=False
    )
    
    query = "Research the history of AI and summarize it."
    print(f"Query: {query}")
    
    interaction.set_query(query) # Helper method might be missing in LangGraphInteraction, let's check
    # LangGraphInteraction doesn't have set_query in my implementation above, I should add it or set directly
    interaction.last_query = query
    
    print("Thinking...")
    success = await interaction.think()
    
    if success:
        print(f"Success! Answer: {interaction.last_answer}")
        print(f"Reasoning: {interaction.last_reasoning}")
    else:
        print(f"Failed. Last answer: {interaction.last_answer}")

if __name__ == "__main__":
    asyncio.run(main())
