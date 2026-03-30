"""Heartbeat ORM model."""

from __future__ import annotations

import datetime
import uuid
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base
from shared.db.settings import DATABASE_SCHEMA


class HeartbeatEvent(Base):
    __tablename__ = "heartbeat_events"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    heartbeat_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    kafka_offsets: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    system_checks: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
