from typing import List, Optional
import time
import uuid
from sqlalchemy import select

from letta.log import get_logger
from letta.orm.environment import Environment as EnvironmentModel, Device as DeviceModel
from letta.orm.errors import NoResultFound
from letta.schemas.environment import Environment as PydanticEnvironment, EnvironmentCreate, EnvironmentUpdate, DeviceMetadata
from letta.schemas.user import User
from letta.server.db import db_registry
from letta.utils import enforce_types

logger = get_logger(__name__)

class EnvironmentManager:
    """Manager class to handle business logic related to Remote Environments."""

    @enforce_types
    async def register_environment_async(self, registration: EnvironmentCreate, actor: User) -> PydanticEnvironment:
        """Register a new remote environment."""
        async with db_registry.async_session() as session:
            connection_id = f"env-{uuid.uuid4()}"
            
            # Ensure device exists or create it? 
            # For now, we'll just focus on the environment/connection
            
            new_env = EnvironmentModel(
                id=connection_id,
                device_id=registration.device_id,
                connection_name=registration.connection_name,
                organization_id=actor.organization_id,
                user_id=actor.id,
                first_seen_at=int(time.time() * 1000),
                last_seen_at=int(time.time() * 1000),
                metadata_=registration.metadata.model_dump()
            )
            
            await new_env.create_async(session)
            return new_env.to_pydantic()

    @enforce_types
    async def get_environment_by_id_async(self, environment_id: str, actor: User) -> PydanticEnvironment:
        """Fetch an environment by ID."""
        async with db_registry.async_session() as session:
            env = await EnvironmentModel.read_async(db_session=session, identifier=environment_id, actor=actor)
            return env.to_pydantic()

    @enforce_types
    async def list_environments_async(self, actor: User) -> List[PydanticEnvironment]:
        """List all environments for an actor's organization."""
        async with db_registry.async_session() as session:
            envs = await EnvironmentModel.list_async(db_session=session, actor=actor)
            return [env.to_pydantic() for env in envs]

    @enforce_types
    async def update_environment_activity_async(self, environment_id: str):
        """Update the last_seen_at timestamp for an environment."""
        async with db_registry.async_session() as session:
            try:
                # We don't necessarily have an actor here (it's a background/system update)
                # But read_async requires one if model has organization_id
                # So we use a direct select
                stmt = select(EnvironmentModel).where(EnvironmentModel.id == environment_id)
                result = await session.execute(stmt)
                env = result.scalar_one_or_none()
                if env:
                    env.last_seen_at = int(time.time() * 1000)
                    await env.update_async(session)
            except Exception as e:
                logger.error(f"Failed to update environment activity for {environment_id}: {e}")
