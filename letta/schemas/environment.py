from typing import Dict, Optional
from pydantic import Field
from letta.schemas.letta_base import LettaBase

class DeviceMetadata(LettaBase):
    os: Optional[str] = Field(None, description="Operating system of the device")
    nodeVersion: Optional[str] = Field(None, description="Node.js version")
    lettaCodeVersion: Optional[str] = Field(None, description="Letta Code version")

class Device(LettaBase):
    id: str = Field(..., description="Unique identifier for the device (UUID)")
    organization_id: str = Field(..., description="Organization ID the device belongs to")
    user_id: str = Field(..., description="User ID who registered the device")

class Environment(LettaBase):
    id: str = Field(..., description="Connection ID")
    device_id: str = Field(..., description="Device ID")
    connection_name: str = Field(..., description="Human-readable name for the environment")
    organization_id: str = Field(..., description="Organization ID")
    user_id: str = Field(..., description="User ID")
    first_seen_at: int = Field(..., description="Timestamp of first appearance")
    last_seen_at: int = Field(..., description="Timestamp of last activity")
    metadata: DeviceMetadata = Field(..., description="Device metadata")

class EnvironmentCreate(LettaBase):
    device_id: str = Field(..., description="Device ID")
    connection_name: str = Field(..., description="Human-readable name for the environment")
    metadata: DeviceMetadata = Field(..., description="Device metadata")

class EnvironmentUpdate(LettaBase):
    connection_name: Optional[str] = None
    metadata: Optional[DeviceMetadata] = None
