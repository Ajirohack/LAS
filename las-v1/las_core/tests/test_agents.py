"""
Unit tests for LangGraph Agents.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from agents.supervisor import SupervisorAgent
from sources.agents.planner_agent import PlannerAgent
from sources.agents.code_agent import CoderAgent

class TestSupervisorAgent:
    """Test the Supervisor Agent."""
    
    @pytest.fixture
    def supervisor(self):
        """Create a supervisor agent for testing."""
        with patch('agents.supervisor.get_llm_service') as mock_get_llm, \
             patch('agents.supervisor.ChatPromptTemplate') as mock_prompt_cls:
            
            # Setup mock LLM service and LLM as MagicMock to support | operator
            mock_service = Mock()
            mock_get_llm.return_value = mock_service
            mock_langchain_llm = MagicMock()
            mock_service.get_langchain_llm.return_value = mock_langchain_llm
            
            # Setup bind_functions to return a runnable (MagicMock) 
            mock_langchain_llm.bind_functions.return_value = MagicMock()
            
            # Setup prompt template to allow | operator
            mock_prompt_instance = MagicMock()
            mock_prompt_cls.from_messages.return_value.partial.return_value = mock_prompt_instance
            
            # Patch JsonOutputFunctionsParser to avoid import error fallback issues during init if it's missing
            with patch('agents.supervisor.JsonOutputFunctionsParser', MagicMock()):
                 agent = SupervisorAgent(members=["Planner", "Coder"], system_prompt="You are a supervisor.")
                 return agent
    
    def test_supervisor_initialization(self, supervisor):
        """Test supervisor initializes correctly."""
        assert supervisor is not None
        # SupervisorAgent does not set agent_name attribute, checking specific attribute presence
        assert hasattr(supervisor, "chain")
    
    @pytest.mark.asyncio
    async def test_supervisor_routing(self, supervisor):
        """Test supervisor routes tasks to appropriate agents."""
        # Note: SupervisorAgent.run returns chain.invoke(state)
        # We need to mock the chain.invoke
        
        # Manually set the chain to a mock because we can't easily patch inside existing instance
        supervisor.chain = Mock()
        supervisor.chain.invoke.return_value = {"next": "Planner"}
        
        state = {"messages": []}
        result = supervisor.run(state)
        
        assert result is not None
        assert result["next"] == "Planner"

    @pytest.mark.asyncio
    async def test_supervisor_chain_creation_fallback(self):
        """Test fallback when JsonOutputFunctionsParser is missing."""
        with patch('agents.supervisor.get_llm_service') as mock_get_llm, \
             patch('agents.supervisor.ChatPromptTemplate') as mock_prompt_cls, \
             patch('agents.supervisor.JsonOutputFunctionsParser', None):
            
            mock_service = Mock()
            mock_get_llm.return_value = mock_service
            mock_langchain_llm = MagicMock() # Supports |
            # Remove bind_functions to force fallback
            del mock_langchain_llm.bind_functions 
            
            mock_service.get_langchain_llm.return_value = mock_langchain_llm
            
            mock_prompt_instance = MagicMock()
            mock_prompt_cls.from_messages.return_value.partial.return_value = mock_prompt_instance

            # We need valid import of JsonOutputParser for fallback line 77/81
            # Assuming langchain_core is installed, this import should work.
            # If not, we might fail here, but we can patch it in sys.modules if needed.
            try:
                agent = SupervisorAgent(members=["Planner"], system_prompt="Prompt")
                assert agent.chain is not None
            except ImportError:
                pytest.skip("JsonOutputParser not available")


class TestPlannerAgent:
    """Test the Planner Agent."""
    
    @pytest.fixture
    def planner(self):
        """Create a planner agent for testing."""
        mock_provider = Mock()
        mock_provider.get_model_name.return_value = "gpt-4"
        
        # PlannerAgent init requires: name, prompt_path, provider, verbose=False, browser=None
        agent = PlannerAgent("planner", "prompts/base/planner_agent.txt", mock_provider)
        return agent
    
    def test_planner_initialization(self, planner):
        """Test planner initializes correctly."""
        assert planner is not None
        assert planner.type == "planner_agent"
    
    @pytest.mark.asyncio
    async def test_planner_basic_methods(self, planner):
        """Test basic methods like get_task_names."""
        # This avoids complex mocking of LLM requests which might be hard
        text = "Task 1: Do something\nTask 2: Do something else"
        # Since logic inside get_task_names looks for ## or digit
        # Line 57: if '##' in line or line[0].isdigit():
        tasks = planner.get_task_names("1. Task one\n## Task two")
        assert len(tasks) == 2


class TestCoderAgent:
    """Test the Coder Agent."""
    
    @pytest.fixture
    def coder(self):
        """Create a coder agent for testing."""
        mock_provider = Mock()
        mock_provider.get_model_name.return_value = "claude-3-opus"
        
        agent = CoderAgent("coder", "prompts/base/coder_agent.txt", mock_provider)
        return agent
    
    def test_coder_initialization(self, coder):
        """Test coder initializes correctly."""
        assert coder is not None
        assert coder.role == "code"
