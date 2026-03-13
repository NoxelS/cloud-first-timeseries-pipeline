from __future__ import annotations

import argparse
import datetime
import logging
import uuid

from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics


def _parse_args() -> argparse.Namespace:
    today = datetime.datetime.now(tz=datetime.timezone.utc).date().isoformat()
    parser = argparse.ArgumentParser(description="Publish a Kafka command to trigger Energy Charts backfill.")
    parser.add_argument("--region", default="DE-Freiburg", help="Energy Charts region (default: DE-Freiburg)")
    parser.add_argument("--start-date", default=today, help="Backfill start date in YYYY-MM-DD (default: today UTC)")
    parser.add_argument("--end-date", default="2023-01-01", help="Backfill end date in YYYY-MM-DD")
    parser.add_argument("--request-id", default=str(uuid.uuid4()), help="Optional request id")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _parse_args()

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "request_id": args.request_id,
        "region": args.region,
        "start_date": args.start_date,
        "end_date": args.end_date,
    }

    publish_event(KafkaTopics.CMD_ENERGY_CHARTS_BACKFILL.value, event)
    logging.info(
        "Published backfill command to %s for region=%s range=%s..%s",
        KafkaTopics.CMD_ENERGY_CHARTS_BACKFILL.value,
        args.region,
        args.start_date,
        args.end_date,
    )


if __name__ == "__main__":
    main()
