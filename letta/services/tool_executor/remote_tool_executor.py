import asyncio
import json
import uuid
from typing import Any, Dict, Optional

from letta.log import get_logger
from letta.schemas.agent import AgentState
from letta.schemas.sandbox_config import SandboxConfig
from letta.schemas.tool import Tool
from letta.schemas.tool_execution_result import ToolExecutionResult
from letta.schemas.user import User
from letta.services.tool_executor.tool_executor_base import ToolExecutor

logger = get_logger(__name__)

class RemoteToolExecutor(ToolExecutor):
    """Executor that forwards tool calls to a remote environment via WebSocket."""

    async def execute(
        self,
        function_name: str,
        function_args: dict,
        tool: Tool,
        actor: User,
        agent_state: Optional[AgentState] = None,
        sandbox_config: Optional[SandboxConfig] = None,
        sandbox_env_vars: Optional[Dict[str, Any]] = None,
    ) -> ToolExecutionResult:
        if not agent_state or not agent_state.environment_id:
            raise ValueError("agent_state and environment_id are required for RemoteToolExecutor")

        # Import manager here to avoid circular imports
        from letta.server.rest_api.routers.v1.environments import manager as ws_manager
        
        request_id = str(uuid.uuid4())
        message = {
            "type": "tool_call",
            "id": request_id,
            "function": {
                "name": function_name,
                "arguments": json.dumps(function_args),
            }
        }

        connection_id = agent_state.environment_id
        logger.info(f"Forwarding tool call {function_name} to remote environment {connection_id}")
        
        # In a real implementation, we'd need a way to wait for the response.
        # Since WebSocket is async, we might need a future map.
        # For now, let's assume we have a way to wait.
        
        # Let's add a response future map to the connection manager or similar.
        # Actually, let's just implement a simple wait for now.
        
        await ws_manager.send_json(connection_id, message)
        
        try:
            response = await ws_manager.wait_for_response(request_id)
            status = response.get("status", "success")
            func_return = response.get("func_return")
            stdout = response.get("stdout", [])
            stderr = response.get("stderr", [])
            
            return ToolExecutionResult(
                status=status,
                func_return=func_return,
                stdout=stdout,
                stderr=stderr,
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for remote tool execution {function_name} from {connection_id}")
            return ToolExecutionResult(
                status="error",
                func_return=f"Timeout waiting for remote tool execution {function_name}",
                stderr=["Timeout waiting for remote response"],
            )

