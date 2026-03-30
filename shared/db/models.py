"""ORM models for shared database tables."""

from __future__ import annotations

import datetime

from sqlalchemy import Date, DateTime, Double, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base
from shared.db.settings import DATABASE_SCHEMA


class EnergyChartsFrequency(Base):
    __tablename__ = "energy_charts_frequency"
    __table_args__ = (
        Index("idx_energy_charts_frequency_event_timestamp", "event_timestamp"),
        {"schema": DATABASE_SCHEMA},
    )

    event_id: Mapped[str] = mapped_column(Text, nullable=False)
    series_id: Mapped[str] = mapped_column(Text, primary_key=True)
    event_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    frequency_hz: Mapped[float | None] = mapped_column(Double, nullable=True)
    source_region: Mapped[str] = mapped_column(Text, nullable=False)
    request_id: Mapped[str] = mapped_column(Text, nullable=False)
    collected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class EnergyChartsIngestionState(Base):
    __tablename__ = "energy_charts_ingestion_state"
    __table_args__ = ({"schema": DATABASE_SCHEMA},)

    series_id: Mapped[str] = mapped_column(String, primary_key=True)
    pipeline_name: Mapped[str] = mapped_column(String, primary_key=True)
    last_ingested_ts: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    backfill_cursor_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="idle")
