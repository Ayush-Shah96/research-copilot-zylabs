"""LangGraph workflow graph definition."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
from app.workflows.states import ResearchState, WorkflowConfig, NODE_METADATA

logger = logging.getLogger(__name__)


class ResearchWorkflow:
    """LangGraph-based research workflow orchestrator."""
    
    def __init__(self, config: Optional[WorkflowConfig] = None):
        """Initialize the workflow with configuration."""
        self.config = config or WorkflowConfig()
        self.execution_history: List[Dict[str, Any]] = []
        
    def should_route_to_retry(self, state: ResearchState) -> str:
        """
        Conditional routing logic: Determine if retry is needed.
        
        Returns:
            "retry" if quality check fails and retries remain
            "report" if quality passes or max retries reached
        """
        requires_retry = state.get("requires_retry", False)
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", self.config.max_retries)
        
        if requires_retry and retry_count < max_retries:
            logger.info(f"Routing to retry (attempt {retry_count + 1}/{max_retries})")
            return "retry"
        
        logger.info("Routing to report generation")
        return "report"
    
    def _log_node_execution(
        self,
        node_name: str,
        status: str,
        state: ResearchState,
        duration: float = 0
    ) -> None:
        """Log node execution details."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": node_name,
            "status": status,
            "duration_seconds": duration,
            "state_keys": list(state.keys()),
        }
        self.execution_history.append(log_entry)
        logger.info(f"Node {node_name} [{status}] - Duration: {duration:.2f}s")
    
    async def execute_node(
        self,
        node_name: str,
        state: ResearchState
    ) -> ResearchState:
        """
        Execute a single node with error handling.
        
        Args:
            node_name: Name of the node to execute
            state: Current workflow state
            
        Returns:
            Updated state after node execution
            
        Raises:
            Exception: If node execution fails after retries
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Executing node: {node_name}")
            
            # Import NODE_FUNCTIONS from nodes module
            from app.workflows.nodes import NODE_FUNCTIONS
            
            # Get the node function from registry
            node_func = NODE_FUNCTIONS.get(node_name)
            if not node_func:
                raise ValueError(f"Unknown node: {node_name}")
            
            # Execute node with timeout
            try:
                metadata = NODE_METADATA.get(node_name)
                node_timeout = metadata.timeout if metadata else 300
                state = await asyncio.wait_for(
                    asyncio.to_thread(node_func, state, self.config),
                    timeout=node_timeout
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"Node {node_name} timed out after {node_timeout}s")
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_node_execution(node_name, "completed", state, duration)
            
            return state
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error in node {node_name}: {str(e)}")
            self._log_node_execution(node_name, "failed", state, duration)
            raise
    
    async def execute(self, initial_state: ResearchState) -> ResearchState:
        """
        Execute the complete research workflow.
        
        Workflow:
        1. Planner → Plan research strategy
        2. Researcher → Collect research data
        3. Analyzer → Analyze findings
        4. Quality Check → Validate quality
        5. (Optional Retry) → Return to Researcher if quality low
        6. Reporter → Generate final report
        
        Args:
            initial_state: Initial workflow state with company info
            
        Returns:
            Final state with complete research report
        """
        logger.info(f"Starting research workflow for {initial_state.get('company_name')}")
        
        # Initialize state metadata
        state = initial_state.copy()
        state["start_time"] = datetime.utcnow().isoformat()
        state["retry_count"] = state.get("retry_count", 0)
        state["max_retries"] = self.config.max_retries
        state["processing_status"] = "started"
        
        try:
            # Node 1: Planner
            state = await self.execute_node("planner", state)
            
            # Retry loop for research quality
            retry_count = 0
            while retry_count <= self.config.max_retries:
                # Node 2: Researcher
                state = await self.execute_node("researcher", state)
                
                # Node 3: Analyzer
                state = await self.execute_node("analyzer", state)
                
                # Node 4: Quality Check
                state = await self.execute_node("quality_check", state)
                
                # Conditional routing
                route = self.should_route_to_retry(state)
                
                if route == "report":
                    break
                
                retry_count += 1
                state["retry_count"] = retry_count
                logger.info(f"Quality check failed, retrying... (attempt {retry_count})")
            
            # Node 5: Reporter
            state = await self.execute_node("reporter", state)
            
            state["processing_status"] = "completed"
            logger.info(f"Research workflow completed successfully")
            
            return state
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            state["error_message"] = str(e)
            state["processing_status"] = "failed"
            raise
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the execution history of the workflow."""
        return self.execution_history
    
    def reset_history(self) -> None:
        """Reset execution history."""
        self.execution_history = []


class WorkflowManager:
    """Manages workflow instances and execution."""
    
    def __init__(self):
        """Initialize the workflow manager."""
        self.active_workflows: Dict[str, ResearchWorkflow] = {}
        self.workflow_states: Dict[str, ResearchState] = {}
    
    def create_workflow(
        self,
        session_id: str,
        config: Optional[WorkflowConfig] = None
    ) -> ResearchWorkflow:
        """Create a new workflow instance."""
        workflow = ResearchWorkflow(config)
        self.active_workflows[session_id] = workflow
        logger.info(f"Created workflow for session {session_id}")
        return workflow
    
    def get_workflow(self, session_id: str) -> Optional[ResearchWorkflow]:
        """Get an existing workflow instance."""
        return self.active_workflows.get(session_id)
    
    def get_state(self, session_id: str) -> Optional[ResearchState]:
        """Get the current state of a workflow."""
        return self.workflow_states.get(session_id)
    
    def save_state(self, session_id: str, state: ResearchState) -> None:
        """Save workflow state."""
        self.workflow_states[session_id] = state
        logger.info(f"State saved for session {session_id}")
    
    def cleanup(self, session_id: str) -> None:
        """Clean up workflow resources."""
        self.active_workflows.pop(session_id, None)
        self.workflow_states.pop(session_id, None)
        logger.info(f"Cleaned up workflow for session {session_id}")


# Global workflow manager instance
workflow_manager = WorkflowManager()