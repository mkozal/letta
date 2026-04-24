import uuid
from typing import Optional
from sqlalchemy import JSON, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from letta.orm.sqlalchemy_base import SqlalchemyBase
from letta.orm.mixins import OrganizationMixin, UserMixin
from letta.schemas.environment import Environment as PydanticEnvironment, Device as PydanticDevice

class Device(SqlalchemyBase, OrganizationMixin, UserMixin):
    __tablename__ = "devices"
    __pydantic_model__ = PydanticDevice

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"dev-{uuid.uuid4()}")
    
    # We might want to store more device-specific info later

class Environment(SqlalchemyBase, OrganizationMixin, UserMixin):
    __tablename__ = "environments"
    __pydantic_model__ = PydanticEnvironment

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"env-{uuid.uuid4()}")
    device_id: Mapped[str] = mapped_column(String, nullable=False)
    connection_name: Mapped[str] = mapped_column(String, nullable=False)
    
    first_seen_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_seen_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # Store DeviceMetadata as JSON
    metadata_: Mapped[dict] = mapped_column(JSON, nullable=False)

    def to_pydantic(self) -> PydanticEnvironment:
        return PydanticEnvironment(
            id=self.id,
            device_id=self.device_id,
            connection_name=self.connection_name,
            organization_id=self.organization_id,
            user_id=self.user_id,
            first_seen_at=self.first_seen_at,
            last_seen_at=self.last_seen_at,
            metadata=self.metadata_
        )
