from shared.db.models import EnergyChartsFrequency, EnergyChartsIngestionState
from shared.db.settings import DATABASE_SCHEMA


def test_frequency_model_uses_raw_schema() -> None:
    assert EnergyChartsFrequency.__table__.schema == DATABASE_SCHEMA
    assert EnergyChartsFrequency.__tablename__ == "energy_charts_frequency"


def test_ingestion_state_model_uses_raw_schema() -> None:
    assert EnergyChartsIngestionState.__table__.schema == DATABASE_SCHEMA
    assert EnergyChartsIngestionState.__tablename__ == "energy_charts_ingestion_state"
