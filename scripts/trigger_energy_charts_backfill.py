from __future__ import annotations

import argparse
import datetime
import logging
import uuid

from shared.config import load_energy_charts_settings
from shared.energy_charts.backfill import resolve_backfill_command
from shared.energy_charts.time import utc_now
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics
from shared.schemas import BackfillCommandPayload


def _parse_args() -> argparse.Namespace:
    today = datetime.datetime.now(tz=datetime.timezone.utc).date().isoformat()
    default_region = load_energy_charts_settings().region
    parser = argparse.ArgumentParser(description="Publish a Kafka command to trigger Energy Charts backfill.")
    parser.add_argument("--region", default=default_region, help=f"Energy Charts region (default: {default_region})")
    parser.add_argument("--start-date", default=today, help="Backfill start date in YYYY-MM-DD (default: today UTC)")
    parser.add_argument("--end-date", default="2023-01-01", help="Backfill end date in YYYY-MM-DD")
    parser.add_argument("--request-id", default=str(uuid.uuid4()), help="Optional request id")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _parse_args()
    command = resolve_backfill_command(
        {
            "region": args.region,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "request_id": args.request_id,
        },
        default_region=load_energy_charts_settings().region,
        default_start_date=datetime.datetime.now(tz=datetime.timezone.utc).date(),
    )

    event = BackfillCommandPayload(
        event_id=str(uuid.uuid4()),
        timestamp=utc_now().isoformat(),
        request_id=command.request_id,
        region=command.region,
        start_date=command.start_date.isoformat(),
        end_date=command.end_date.isoformat(),
    ).to_dict()

    publish_event(KafkaTopics.CMD_ENERGY_CHARTS_BACKFILL.value, event)
    logging.info(
        "Published backfill command to %s for region=%s range=%s..%s",
        KafkaTopics.CMD_ENERGY_CHARTS_BACKFILL.value,
        command.region,
        command.start_date.isoformat(),
        command.end_date.isoformat(),
    )


if __name__ == "__main__":
    main()
