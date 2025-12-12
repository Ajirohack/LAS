"""
Workflow Management - Create and execute custom agent workflows.

This module provides a complete workflow execution engine that:
1. Traverses nodes in order defined by edges
2. Executes each node (agent call, tool call, etc.)
3. Passes state between nodes
4. Handles branching/decisions
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum
import json
import uuid
import asyncio
from datetime import datetime

from sources.logger import Logger

router = APIRouter()
logger = Logger("workflows.log")


class NodeType(str, Enum):
    START = "start"
    END = "end"
    AGENT = "agent"
    TOOL = "tool"
    DECISION = "decision"
    TRANSFORM = "transform"
    DELAY = "delay"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowNode(BaseModel):
    id: str
    type: str  # start, end, agent, tool, decision, transform, delay
    position: Dict[str, float]
    data: Dict[str, Any]


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None  # Used for decision branches (e.g., "yes", "no", "default")


class Workflow(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ExecutionResult(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    current_node: Optional[str] = None
    outputs: Dict[str, Any] = {}
    errors: List[str] = []
    node_results: Dict[str, Any] = {}


class WorkflowExecutionEngine:
    """
    Executes workflows by traversing nodes and edges.
    
    Supports node types:
    - start: Entry point, passes inputs to next node
    - end: Exit point, returns final outputs
    - agent: Invokes an LLM agent (planner, coder, websurfer)
    - tool: Executes a tool command
    - decision: Branches based on condition evaluation
    - transform: Transforms data using JavaScript-like expressions
    - delay: Adds a delay before continuing
    """
    
    def __init__(self):
        self._executions: Dict[str, ExecutionResult] = {}
    
    async def execute(self, workflow: Workflow, inputs: Dict[str, Any]) -> ExecutionResult:
        """Execute a workflow with given inputs."""
        execution_id = str(uuid.uuid4())
        
        result = ExecutionResult(
            execution_id=execution_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now().isoformat(),
            outputs={"inputs": inputs}
        )
        self._executions[execution_id] = result
        
        try:
            # Build node and edge maps for efficient lookup
            nodes = {node.id: node for node in workflow.nodes}
            edges_from = {}  # source_id -> list of edges
            for edge in workflow.edges:
                if edge.source not in edges_from:
                    edges_from[edge.source] = []
                edges_from[edge.source].append(edge)
            
            # Find start node
            start_node = self._find_start_node(nodes)
            if not start_node:
                raise ValueError("Workflow must have a 'start' node")
            
            # Initialize execution state
            state = {
                "inputs": inputs,
                "messages": [],
                "variables": {},
                **inputs
            }
            
            # Execute workflow
            current_node_id = start_node.id
            visited = set()
            max_iterations = 100  # Prevent infinite loops
            iteration = 0
            
            while current_node_id and iteration < max_iterations:
                iteration += 1
                
                if current_node_id in visited and nodes[current_node_id].type != NodeType.DECISION:
                    logger.warning(f"Cycle detected at node {current_node_id}, breaking")
                    break
                visited.add(current_node_id)
                
                current_node = nodes.get(current_node_id)
                if not current_node:
                    raise ValueError(f"Node {current_node_id} not found")
                
                result.current_node = current_node_id
                logger.info(f"Executing node: {current_node_id} (type: {current_node.type})")
                
                # Execute the node
                node_output, next_label = await self._execute_node(current_node, state)
                result.node_results[current_node_id] = node_output
                
                # Update state with node output
                if isinstance(node_output, dict):
                    state["variables"].update(node_output)
                    state.update(node_output)
                
                # Check for end node
                if current_node.type == NodeType.END:
                    result.outputs = {
                        "final": node_output,
                        "state": state.get("variables", {})
                    }
                    break
                
                # Find next node
                current_node_id = self._find_next_node(current_node_id, edges_from, next_label)
            
            result.status = ExecutionStatus.COMPLETED
            result.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            result.status = ExecutionStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.now().isoformat()
        
        self._executions[execution_id] = result
        return result
    
    def _find_start_node(self, nodes: Dict[str, WorkflowNode]) -> Optional[WorkflowNode]:
        """Find the start node in the workflow."""
        for node in nodes.values():
            if node.type == NodeType.START:
                return node
        return None
    
    def _find_next_node(self, current_id: str, edges_from: Dict[str, List[WorkflowEdge]], 
                        label: Optional[str] = None) -> Optional[str]:
        """Find the next node ID based on edges and optional label (for decisions)."""
        edges = edges_from.get(current_id, [])
        
        if not edges:
            return None
        
        # If label specified, find matching edge
        if label:
            for edge in edges:
                if edge.label and edge.label.lower() == label.lower():
                    return edge.target
            # Fallback to default edge if no match
            for edge in edges:
                if edge.label and edge.label.lower() == "default":
                    return edge.target
        
        # Return first edge target (default path)
        return edges[0].target
    
    async def _execute_node(self, node: WorkflowNode, state: Dict[str, Any]) -> tuple:
        """
        Execute a single node and return (output, next_label).
        
        Returns:
            tuple: (node_output, label_for_next_edge)
        """
        node_type = node.type
        data = node.data
        
        if node_type == NodeType.START:
            # Start node: just pass through inputs
            return state.get("inputs", {}), None
        
        elif node_type == NodeType.END:
            # End node: collect and return final output
            output_key = data.get("output_key", "result")
            return {output_key: state.get("variables", {})}, None
        
        elif node_type == NodeType.AGENT:
            return await self._execute_agent_node(data, state)
        
        elif node_type == NodeType.TOOL:
            return await self._execute_tool_node(data, state)
        
        elif node_type == NodeType.DECISION:
            return await self._execute_decision_node(data, state)
        
        elif node_type == NodeType.TRANSFORM:
            return self._execute_transform_node(data, state)
        
        elif node_type == NodeType.DELAY:
            delay_seconds = data.get("seconds", 1)
            await asyncio.sleep(delay_seconds)
            return {"delayed": delay_seconds}, None
        
        else:
            logger.warning(f"Unknown node type: {node_type}")
            return {}, None
    
    async def _execute_agent_node(self, data: Dict[str, Any], state: Dict[str, Any]) -> tuple:
        """Execute an agent node."""
        agent_type = data.get("agent_type", "planner")
        prompt = data.get("prompt", "")
        
        # Substitute variables in prompt
        prompt = self._substitute_variables(prompt, state)
        
        try:
            from langchain_core.messages import HumanMessage
            
            if agent_type == "planner":
                from agents.workers.planner import PlannerAgent
                agent = PlannerAgent()
                result = agent.run({"messages": [HumanMessage(content=prompt)]})
                return {"agent_response": result.get("plan", ""), "messages": result.get("messages", [])}, None
            
            elif agent_type == "coder":
                from agents.workers.coder import CoderAgent
                agent = CoderAgent()
                result = agent.run({"messages": [HumanMessage(content=prompt)]})
                return {"agent_response": result["messages"][-1].content if result.get("messages") else ""}, None
            
            elif agent_type == "websurfer":
                from agents.workers.web_surfer import WebSurferAgent
                agent = WebSurferAgent()
                result = await agent.run({"messages": [HumanMessage(content=prompt)]})
                return {"agent_response": result["messages"][-1].content if result.get("messages") else ""}, None
            
            else:
                # Generic LLM call
                from services.llm_service import get_llm_service
                llm_service = get_llm_service()
                llm = llm_service.get_langchain_llm()
                response = llm.invoke([HumanMessage(content=prompt)])
                return {"agent_response": response.content}, None
                
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {"error": str(e)}, None
    
    async def _execute_tool_node(self, data: Dict[str, Any], state: Dict[str, Any]) -> tuple:
        """Execute a tool command."""
        command = data.get("command", "")
        args = data.get("args", {})
        
        # Substitute variables in args
        resolved_args = {}
        for key, value in args.items():
            if isinstance(value, str):
                resolved_args[key] = self._substitute_variables(value, state)
            else:
                resolved_args[key] = value
        
        try:
            from services.tool_service import get_tool_service
            tool_service = get_tool_service()
            result = await tool_service.execute_command(command, **resolved_args)
            return {"tool_result": result}, None
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": str(e)}, None
    
    async def _execute_decision_node(self, data: Dict[str, Any], state: Dict[str, Any]) -> tuple:
        """
        Execute a decision node that evaluates a condition.
        
        Supports:
        - Simple comparisons: "variable == value"
        - Contains check: "keyword in variable"
        - LLM-based decisions: Uses LLM to evaluate complex conditions
        """
        condition = data.get("condition", "")
        use_llm = data.get("use_llm", False)
        
        if use_llm:
            # Use LLM to evaluate condition
            try:
                from services.llm_service import get_llm_service
                from langchain_core.messages import HumanMessage
                
                llm_service = get_llm_service()
                llm = llm_service.get_langchain_llm()
                
                prompt = f"""Evaluate this condition and respond with ONLY 'yes' or 'no':

Condition: {condition}

Current state/context:
{json.dumps(state.get('variables', {}), indent=2)}

Answer (yes/no):"""
                
                response = llm.invoke([HumanMessage(content=prompt)])
                answer = response.content.strip().lower()
                
                if "yes" in answer:
                    return {"decision": "yes"}, "yes"
                else:
                    return {"decision": "no"}, "no"
                    
            except Exception as e:
                logger.error(f"LLM decision failed: {e}")
                return {"error": str(e)}, "default"
        
        else:
            # Simple condition evaluation
            try:
                # Substitute variables in condition
                resolved_condition = self._substitute_variables(condition, state)
                
                # Safe evaluation of simple conditions
                variables = state.get("variables", {})
                
                # Check for common patterns
                if " == " in resolved_condition:
                    parts = resolved_condition.split(" == ", 1)
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    left_val = str(variables.get(left, left))
                    result = left_val == right
                    
                elif " != " in resolved_condition:
                    parts = resolved_condition.split(" != ", 1)
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    left_val = str(variables.get(left, left))
                    result = left_val != right
                    
                elif " in " in resolved_condition:
                    parts = resolved_condition.split(" in ", 1)
                    keyword = parts[0].strip().strip("'\"")
                    var_name = parts[1].strip()
                    var_val = str(variables.get(var_name, var_name))
                    result = keyword in var_val
                    
                elif " > " in resolved_condition:
                    parts = resolved_condition.split(" > ", 1)
                    left = float(variables.get(parts[0].strip(), parts[0].strip()))
                    right = float(parts[1].strip())
                    result = left > right
                    
                elif " < " in resolved_condition:
                    parts = resolved_condition.split(" < ", 1)
                    left = float(variables.get(parts[0].strip(), parts[0].strip()))
                    right = float(parts[1].strip())
                    result = left < right
                    
                else:
                    # Check if variable is truthy
                    result = bool(variables.get(resolved_condition, False))
                
                label = "yes" if result else "no"
                return {"decision": label, "condition": resolved_condition}, label
                
            except Exception as e:
                logger.error(f"Condition evaluation failed: {e}")
                return {"error": str(e)}, "default"
    
    def _execute_transform_node(self, data: Dict[str, Any], state: Dict[str, Any]) -> tuple:
        """
        Execute a transform node that manipulates data.
        
        Supports:
        - set: Set a variable to a value
        - append: Append to a list
        - extract: Extract a field from a dict
        - template: String template substitution
        """
        operation = data.get("operation", "set")
        target = data.get("target", "result")
        value = data.get("value", "")
        source = data.get("source", "")
        
        variables = state.get("variables", {})
        
        try:
            if operation == "set":
                # Set variable to value (with substitution)
                resolved_value = self._substitute_variables(str(value), state)
                return {target: resolved_value}, None
            
            elif operation == "append":
                # Append value to list
                existing = variables.get(target, [])
                if not isinstance(existing, list):
                    existing = [existing] if existing else []
                resolved_value = self._substitute_variables(str(value), state)
                existing.append(resolved_value)
                return {target: existing}, None
            
            elif operation == "extract":
                # Extract field from source dict
                source_val = variables.get(source, {})
                field = data.get("field", "")
                if isinstance(source_val, dict):
                    return {target: source_val.get(field, "")}, None
                return {target: ""}, None
            
            elif operation == "template":
                # String template with variable substitution
                template = data.get("template", "")
                resolved = self._substitute_variables(template, state)
                return {target: resolved}, None
            
            elif operation == "concat":
                # Concatenate multiple values
                values = data.get("values", [])
                separator = data.get("separator", " ")
                resolved_values = [self._substitute_variables(str(v), state) for v in values]
                return {target: separator.join(resolved_values)}, None
            
            else:
                return {target: value}, None
                
        except Exception as e:
            logger.error(f"Transform failed: {e}")
            return {"error": str(e)}, None
    
    def _substitute_variables(self, text: str, state: Dict[str, Any]) -> str:
        """Substitute {{variable}} patterns with actual values from state."""
        import re
        
        variables = state.get("variables", {})
        inputs = state.get("inputs", {})
        
        # Merge for lookup
        all_vars = {**inputs, **variables}
        
        def replace_var(match):
            var_name = match.group(1).strip()
            # Support nested access like "result.field"
            parts = var_name.split(".")
            value = all_vars
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, "")
                else:
                    value = ""
                    break
            return str(value)
        
        # Match {{variable}} or {{ variable }}
        pattern = r"\{\{\s*([^}]+)\s*\}\}"
        return re.sub(pattern, replace_var, text)
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get execution result by ID."""
        return self._executions.get(execution_id)
    
    def list_executions(self, workflow_id: Optional[str] = None) -> List[ExecutionResult]:
        """List all executions, optionally filtered by workflow ID."""
        executions = list(self._executions.values())
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        return executions


class WorkflowStorage:
    """Store workflows."""
    
    def __init__(self, storage_dir: str = "data/workflows"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_workflow(self, workflow: Workflow) -> str:
        """Save a workflow."""
        if not workflow.id:
            workflow.id = str(uuid.uuid4())
        
        now = datetime.now().isoformat()
        if not workflow.created_at:
            workflow.created_at = now
        workflow.updated_at = now
        
        workflow_file = self.storage_dir / f"{workflow.id}.json"
        with open(workflow_file, 'w') as f:
            json.dump(workflow.dict(), f, indent=2)
        
        return workflow.id
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        workflow_file = self.storage_dir / f"{workflow_id}.json"
        
        if not workflow_file.exists():
            return None
        
        with open(workflow_file, 'r') as f:
            data = json.load(f)
        
        return Workflow(**data)
    
    def list_workflows(self) -> List[Workflow]:
        """List all workflows."""
        workflows = []
        
        for workflow_file in self.storage_dir.glob("*.json"):
            try:
                with open(workflow_file, 'r') as f:
                    data = json.load(f)
                workflows.append(Workflow(**data))
            except:
                pass
        
        return workflows
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        workflow_file = self.storage_dir / f"{workflow_id}.json"
        
        if workflow_file.exists():
            workflow_file.unlink()
            return True
        
        return False


# Singletons
_storage = WorkflowStorage()
_engine = WorkflowExecutionEngine()


# --- API Endpoints ---

@router.post("/workflows")
async def create_workflow(workflow: Workflow):
    """Create or update a workflow."""
    try:
        workflow_id = _storage.save_workflow(workflow)
        return {"id": workflow_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def list_workflows():
    """List all workflows."""
    try:
        workflows = _storage.list_workflows()
        return {"workflows": [w.dict() for w in workflows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a specific workflow."""
    try:
        workflow = _storage.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow."""
    try:
        success = _storage.delete_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, inputs: Dict[str, Any] = {}):
    """
    Execute a workflow with given inputs.
    
    The workflow engine will:
    1. Find the start node
    2. Traverse nodes following edges
    3. Execute each node (agents, tools, decisions, transforms)
    4. Pass state between nodes
    5. Handle branching based on decision outcomes
    6. Return final outputs when reaching end node
    
    Example inputs:
    ```json
    {
        "query": "Search for Python tutorials",
        "max_results": 5
    }
    ```
    """
    try:
        workflow = _storage.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Execute the workflow
        result = await _engine.execute(workflow, inputs)
        
        return {
            "execution_id": result.execution_id,
            "workflow_id": result.workflow_id,
            "status": result.status,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "outputs": result.outputs,
            "errors": result.errors,
            "node_results": result.node_results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}/executions")
async def list_workflow_executions(workflow_id: str):
    """List all executions for a workflow."""
    try:
        executions = _engine.list_executions(workflow_id)
        return {
            "workflow_id": workflow_id,
            "executions": [
                {
                    "execution_id": e.execution_id,
                    "status": e.status,
                    "started_at": e.started_at,
                    "completed_at": e.completed_at
                }
                for e in executions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get details of a specific execution."""
    try:
        result = _engine.get_execution(execution_id)
        if not result:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "execution_id": result.execution_id,
            "workflow_id": result.workflow_id,
            "status": result.status,
            "current_node": result.current_node,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "outputs": result.outputs,
            "errors": result.errors,
            "node_results": result.node_results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
