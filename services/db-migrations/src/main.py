from __future__ import annotations

import logging
import os
import subprocess
import sys
from collections.abc import Iterable

from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector

from shared.db.base import Base
from shared.db.models import EnergyChartsFrequency
from shared.db.session import create_engine
from shared.db.settings import DATABASE_SCHEMA, load_database_settings

logger = logging.getLogger(__name__)


class MigrationVerificationError(RuntimeError):
    """Raised when migration validation or schema verification fails."""


def _atlas_env() -> dict[str, str]:
    return {
        "ATLAS_DATABASE_URL": load_database_settings().atlas_url,
    }


def _run(command: list[str]) -> None:
    logger.info("Running command: %s", " ".join(command))
    completed = subprocess.run(  # noqa: S603
        command,
        check=False,
        text=True,
        env=os.environ | _atlas_env(),
        capture_output=True,
    )
    if completed.stdout:
        logger.info(completed.stdout.strip())
    if completed.stderr:
        logger.info(completed.stderr.strip())
    if completed.returncode != 0:
        raise MigrationVerificationError(  # noqa: TRY003
            f"Command failed with exit code {completed.returncode}: {' '.join(command)}"
        )


def _expected_tables() -> dict[str, type[Base]]:
    return {mapper.class_.__tablename__: mapper.class_ for mapper in Base.registry.mappers}


def _expected_columns(model: type[Base]) -> dict[str, tuple[str, bool]]:
    columns: dict[str, tuple[str, bool]] = {}
    for column in model.__table__.columns:
        columns[column.name] = (_normalize_type_name(str(column.type)), bool(column.nullable))
    return columns


def _actual_columns(inspector: Inspector, table_name: str) -> dict[str, tuple[str, bool]]:
    columns: dict[str, tuple[str, bool]] = {}
    for column in inspector.get_columns(table_name, schema=DATABASE_SCHEMA):
        columns[column["name"]] = (_normalize_type_name(str(column["type"])), bool(column["nullable"]))
    return columns


def _normalize_type_name(type_name: str) -> str:
    normalized = type_name.lower()
    replacements = {
        "datetime": "timestamp",
        "timestamp with time zone": "timestamp",
        "timestamptz": "timestamp",
        "double": "double precision",
        "double precision": "double precision",
        "varchar": "character varying",
        "string": "character varying",
    }
    return replacements.get(normalized, normalized)


def _compare_indexes(inspector: Inspector, table_name: str, expected_index_names: Iterable[str]) -> None:
    actual = {index["name"] for index in inspector.get_indexes(table_name, schema=DATABASE_SCHEMA)}
    missing = set(expected_index_names) - actual
    if missing:
        missing_csv = ", ".join(sorted(missing))
        raise MigrationVerificationError(  # noqa: TRY003
            f"Missing indexes for {DATABASE_SCHEMA}.{table_name}: {missing_csv}"
        )


def verify_schema() -> None:
    engine = create_engine()
    inspector = inspect(engine)
    tables = set(inspector.get_table_names(schema=DATABASE_SCHEMA))
    expected_tables = _expected_tables()
    missing_tables = set(expected_tables) - tables
    if missing_tables:
        missing_csv = ", ".join(sorted(missing_tables))
        raise MigrationVerificationError(  # noqa: TRY003
            f"Missing tables in schema '{DATABASE_SCHEMA}': {missing_csv}"
        )

    for table_name, model in expected_tables.items():
        expected = _expected_columns(model)
        actual = _actual_columns(inspector, table_name)
        if expected != actual:
            raise MigrationVerificationError(  # noqa: TRY003
                f"Column mismatch for {DATABASE_SCHEMA}.{table_name}: expected={expected!r} actual={actual!r}"
            )

    _compare_indexes(inspector, EnergyChartsFrequency.__tablename__, {"idx_energy_charts_frequency_event_timestamp"})
    engine.dispose()

    logger.info("Schema verification succeeded for schema '%s'", DATABASE_SCHEMA)


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    _run(["atlas", "migrate", "validate", "--env", "docker"])
    _run(["atlas", "migrate", "apply", "--env", "docker"])
    _run(["atlas", "migrate", "status", "--env", "docker"])
    verify_schema()


if __name__ == "__main__":
    try:
        run()
    except Exception:
        logger.exception("Migration runner failed")
        sys.exit(1)
