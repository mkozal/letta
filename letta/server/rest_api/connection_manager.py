import asyncio
import json
from typing import Dict
from fastapi import WebSocket
from letta.log import get_logger

logger = get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        # connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # request_id -> asyncio.Future
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def connect(self, connection_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_json(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json(message)
        else:
            logger.warning(f"Attempted to send message to inactive connection: {connection_id}")

    async def wait_for_response(self, request_id: str, timeout: float = 30.0) -> dict:
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]

    def resolve_response(self, request_id: str, response: dict):
        if request_id in self.pending_requests:
            if not self.pending_requests[request_id].done():
                self.pending_requests[request_id].set_result(response)
