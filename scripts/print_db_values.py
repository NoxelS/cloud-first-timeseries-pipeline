from __future__ import annotations

from sqlalchemy import select

from shared.db.models import EnergyChartsFrequency, EnergyChartsIngestionState
from shared.db.session import session_scope


def main() -> None:
    with session_scope() as session:
        frequency_rows = session.execute(
            select(EnergyChartsFrequency).order_by(EnergyChartsFrequency.event_timestamp.desc()).limit(10)
        ).scalars()
        state_rows = session.execute(select(EnergyChartsIngestionState)).scalars()

        print("Latest frequency rows:")
        for row in frequency_rows:
            print(row.series_id, row.event_timestamp.isoformat(), row.frequency_hz)

        print("\nIngestion state rows:")
        for row in state_rows:
            print(row.series_id, row.pipeline_name, row.last_ingested_ts, row.status)


if __name__ == "__main__":
    main()
