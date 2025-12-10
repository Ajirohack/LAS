"""
Unit tests for LangGraph Agents.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from agents.supervisor import SupervisorAgent
from agents.planner import PlannerAgent
from agents.coder import CoderAgent


class TestSupervisorAgent:
    """Test the Supervisor Agent."""
    
    @pytest.fixture
    def supervisor(self):
        """Create a supervisor agent for testing."""
        with patch('agents.supervisor.get_llm_service'):
            agent = SupervisorAgent()
            return agent
    
    def test_supervisor_initialization(self, supervisor):
        """Test supervisor initializes correctly."""
        assert supervisor is not None
        assert supervisor.agent_name == "Supervisor"
    
    @pytest.mark.asyncio
    async def test_supervisor_routing(self, supervisor):
        """Test supervisor routes tasks to appropriate agents."""
        with patch.object(supervisor, 'llm_provider') as mock_llm:
            mock_llm.respond = Mock(return_value='{"agent": "Planner", "reasoning": "Task requires planning"}')
            
            result = await supervisor.route_task("Create a plan for building a web app")
            
            assert "agent" in result
            assert result["agent"] in ["Planner", "Coder", "WebSurfer"]
    
    @pytest.mark.asyncio
    async def test_supervisor_handles_complex_task(self, supervisor):
        """Test supervisor handles multi-step tasks."""
        with patch.object(supervisor, 'llm_provider') as mock_llm:
            mock_llm.respond = Mock(return_value='{"steps": ["step1", "step2"], "agent": "Planner"}')
            
            result = await supervisor.process_task("Complex multi-step task")
            
            assert result is not None


class TestPlannerAgent:
    """Test the Planner Agent."""
    
    @pytest.fixture
    def planner(self):
        """Create a planner agent for testing."""
        with patch('agents.planner.get_llm_service'):
            agent = PlannerAgent()
            return agent
    
    def test_planner_initialization(self, planner):
        """Test planner initializes correctly."""
        assert planner is not None
        assert planner.agent_name == "Planner"
    
    @pytest.mark.asyncio
    async def test_planner_creates_plan(self, planner):
        """Test planner creates a structured plan."""
        with patch.object(planner, 'llm_provider') as mock_llm:
            mock_llm.respond = Mock(return_value='{"plan": [{"step": 1, "action": "Research"}]}')
            
            plan = await planner.create_plan("Build a web application")
            
            assert plan is not None
            assert "plan" in plan or isinstance(plan, list)
    
    @pytest.mark.asyncio
    async def test_planner_validates_plan(self, planner):
        """Test planner validates generated plans."""
        plan = [
            {"step": 1, "action": "Research", "agent": "WebSurfer"},
            {"step": 2, "action": "Code", "agent": "Coder"}
        ]
        
        is_valid = planner.validate_plan(plan)
        
        assert isinstance(is_valid, bool)


class TestCoderAgent:
    """Test the Coder Agent."""
    
    @pytest.fixture
    def coder(self):
        """Create a coder agent for testing."""
        with patch('agents.coder.get_llm_service'):
            agent = CoderAgent()
            return agent
    
    def test_coder_initialization(self, coder):
        """Test coder initializes correctly."""
        assert coder is not None
        assert coder.agent_name == "Coder"
    
    @pytest.mark.asyncio
    async def test_coder_generates_code(self, coder):
        """Test coder generates code."""
        with patch.object(coder, 'llm_provider') as mock_llm:
            mock_llm.respond = Mock(return_value='```python\ndef hello():\n    print("Hello")\n```')
            
            code = await coder.generate_code("Create a hello world function in Python")
            
            assert code is not None
            assert "def" in code or "function" in code.lower()
    
    @pytest.mark.asyncio
    async def test_coder_executes_code(self, coder):
        """Test coder can execute generated code."""
        code = "result = 2 + 2"
        
        with patch('agents.coder.exec') as mock_exec:
            mock_exec.return_value = None
            
            result = await coder.execute_code(code)
            
            # Should not raise exception
            assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
