import json
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from letta.server.rest_api.dependencies import HeaderParams, get_headers, get_letta_server
from letta.server.server import SyncServer
from letta.schemas.environment import Environment, EnvironmentCreate, DeviceMetadata, EnvironmentList
from letta.log import get_logger

router = APIRouter(prefix="/environments", tags=["environments"])
logger = get_logger(__name__)

@router.get("/", response_model=EnvironmentList, operation_id="list_environments")
async def list_environments(
    server: SyncServer = Depends(get_letta_server),
    headers: HeaderParams = Depends(get_headers),
):
    """List all registered remote environments."""
    actor = await server.user_manager.get_actor_or_default_async(actor_id=headers.actor_id)
    envs = await server.environment_manager.list_environments_async(actor=actor)
    return EnvironmentList(connections=envs, hasNextPage=False)

@router.post("/register", response_model=Environment, operation_id="register_environment")
async def register_environment(
    registration: EnvironmentCreate,
    server: SyncServer = Depends(get_letta_server),
    headers: HeaderParams = Depends(get_headers),
):
    """Register a new remote environment and return its connection ID."""
    actor = await server.user_manager.get_actor_or_default_async(actor_id=headers.actor_id)
    return await server.environment_manager.register_environment_async(registration=registration, actor=actor)

@router.websocket("/ws/{connection_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    connection_id: str,
    server: SyncServer = Depends(get_letta_server),
):
    """WebSocket endpoint for remote environments to listen for instructions."""
    # TODO: Proper auth for WebSocket
    await server.connection_manager.connect(connection_id, websocket)
    try:
        while True:
            # We mostly expect heartbeats or tool results from the client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Update last seen activity
                await server.environment_manager.update_environment_activity_async(connection_id)
                
                # Handle incoming message kinds if any
                if message.get("type") == "tool_return":
                    request_id = message.get("id")
                    if request_id:
                        server.connection_manager.resolve_response(request_id, message)
                
                logger.debug(f"Received WebSocket message from {connection_id}: {message}")
            except json.JSONDecodeError:
                logger.error(f"Received invalid JSON from {connection_id}")
    except WebSocketDisconnect:
        server.connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        server.connection_manager.disconnect(connection_id)
