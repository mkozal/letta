from typing import Dict, List, Optional
from pydantic import Field
from letta.schemas.letta_base import LettaBase

class DeviceMetadata(LettaBase):
    os: Optional[str] = Field(None, description="Operating system of the device")
    node_version: Optional[str] = Field(None, description="Node.js version", alias="nodeVersion")
    letta_code_version: Optional[str] = Field(None, description="Letta Code version", alias="lettaCodeVersion")

class Device(LettaBase):
    id: str = Field(..., description="Unique identifier for the device (UUID)")
    organization_id: str = Field(..., description="Organization ID the device belongs to", alias="organizationId")
    user_id: str = Field(..., description="User ID who registered the device", alias="userId")

class Environment(LettaBase):
    id: str = Field(..., description="Connection ID", alias="connectionId")
    device_id: str = Field(..., description="Device ID", alias="deviceId")
    connection_name: str = Field(..., description="Human-readable name for the environment", alias="connectionName")
    organization_id: str = Field(..., description="Organization ID", alias="organizationId")
    user_id: str = Field(..., description="User ID", alias="userId")
    first_seen_at: int = Field(..., description="Timestamp of first appearance", alias="firstSeenAt")
    last_seen_at: int = Field(..., description="Timestamp of last activity", alias="lastSeenAt")
    metadata: DeviceMetadata = Field(..., description="Device metadata")
    connected_at: Optional[int] = Field(None, description="Timestamp when the environment connected", alias="connectedAt")
    last_heartbeat: Optional[int] = Field(None, description="Timestamp of last heartbeat", alias="lastHeartbeat")
    ws_url: Optional[str] = Field(None, description="WebSocket URL for the environment", alias="wsUrl")

class EnvironmentList(LettaBase):
    connections: List[Environment]
    hasNextPage: bool = Field(False, alias="hasNextPage")

class EnvironmentCreate(LettaBase):
    device_id: str = Field(..., description="Device ID", alias="deviceId")
    connection_name: str = Field(..., description="Human-readable name for the environment", alias="connectionName")
    metadata: DeviceMetadata = Field(..., description="Device metadata")

class EnvironmentUpdate(LettaBase):
    connection_name: Optional[str] = Field(None, alias="connectionName")
    metadata: Optional[DeviceMetadata] = None
