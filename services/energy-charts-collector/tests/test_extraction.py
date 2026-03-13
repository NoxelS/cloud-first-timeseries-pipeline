from __future__ import annotations

import datetime

import collector
from energy_charts_api_client.models.http_validation_error import HTTPValidationError


def test_build_raw_events_filters_to_window():
    unix_seconds = [
        1651363200,  # 2022-05-01 00:00:00
        1651363201,  # 2022-05-01 00:00:01
        1651363500,  # 2022-05-01 00:05:00 (excluded)
    ]
    values = [50.0, None, 50.2]

    window_start = datetime.datetime(2022, 5, 1, 0, 0, tzinfo=datetime.timezone.utc)
    window_end = datetime.datetime(2022, 5, 1, 0, 5, tzinfo=datetime.timezone.utc)
    collected_at = datetime.datetime(2022, 5, 1, 0, 5, tzinfo=datetime.timezone.utc)

    events = collector.build_raw_events(
        unix_seconds=unix_seconds,
        values=values,
        region="DE-Freiburg",
        request_id="r1",
        window_start=window_start,
        window_end=window_end,
        collected_at=collected_at,
    )

    assert len(events) == 2
    assert events[0]["series_id"] == "de-freiburg::grid_frequency"
    assert events[0]["frequency_hz"] == 50.0
    assert events[1]["frequency_hz"] is None


def test_handle_collection_command_persists_aggregated_rows(mocker):
    class StubResponse:
        unix_seconds = [1651363200, 1651363201, 1651363500]
        data = [50.0, 50.2, None]

    mocker.patch(
        "energy_charts_api_client.api.power.frequency_frequency_get.sync",
        return_value=StubResponse(),
    )

    published = []

    def _fake_publish(topic, payload):
        published.append((topic, payload))

    mocker.patch("collector.publish_event", side_effect=_fake_publish)

    n = collector.handle_collection_command(
        {
            "request_id": "r1",
            "datasets": "all",
            "timestamp": "2022-05-01T00:05:00+00:00",
        }
    )

    assert n == 2
    assert len(published) == 2


def test_handle_collection_command_handles_validation_error(mocker):
    mocker.patch(
        "energy_charts_api_client.api.power.frequency_frequency_get.sync",
        return_value=HTTPValidationError(),
    )
    mocker.patch("collector.publish_event")

    n = collector.handle_collection_command(
        {"request_id": "r1", "datasets": "all", "timestamp": "2022-05-01T00:05:00+00:00"}
    )

    assert n == 0
    collector.publish_event.assert_not_called()
