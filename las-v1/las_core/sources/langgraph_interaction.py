from agents.hierarchical_graph import graph
from langchain_core.messages import HumanMessage
from sources.logger import Logger

logger = Logger("langgraph_interaction.log")

class LangGraphInteraction:
    def __init__(self, agents=None, tts_enabled=False, stt_enabled=False, recover_last_session=False, langs=["en"]):
        self.graph = graph
        self.last_query = None
        self.last_answer = None
        self.last_reasoning = None
        self.last_success = False
        self.current_agent = None # Placeholder to satisfy API
        self.agents = agents or [] # Placeholder
        self.recover_last_session = recover_last_session
        self.tts_enabled = tts_enabled
        
    def set_query(self, query):
        self.last_query = query
        
    async def think(self):
        if not self.last_query:
            return False
            
        try:
            inputs = {"messages": [HumanMessage(content=self.last_query)]}
            # Invoke the graph
            # Note: graph.invoke is synchronous, but we can wrap it or use astream
            # For now, let's use invoke. If it blocks too long, we might need astream.
            result = self.graph.invoke(inputs)
            
            # Extract the final answer
            messages = result["messages"]
            last_message = messages[-1]
            self.last_answer = last_message.content
            self.last_reasoning = f"Processed by {last_message.name if hasattr(last_message, 'name') else 'Agent'}"
            self.last_success = True
            
            # Mock current agent for UI compatibility
            class MockAgent:
                def __init__(self, name):
                    self.agent_name = name
                def get_blocks_result(self):
                    return []
            
            self.current_agent = MockAgent(last_message.name if hasattr(last_message, 'name') else "System")
            
            return True
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            self.last_answer = f"Error executing agent graph: {e}"
            self.last_success = False
            return False

    def get_interaction(self):
        return self

    def speak_answer(self):
        # TODO: Implement TTS if needed
        pass

    def save_session(self):
        # TODO: Implement persistence
        pass
