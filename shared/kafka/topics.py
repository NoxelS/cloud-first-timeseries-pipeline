"""Shared topic-name constants and an Enum of all topics.

Keep module-level string constants for backward compatibility and also
export a `KafkaTopics` enum for clearer usage in code.
"""

from __future__ import annotations

from enum import Enum


class KafkaTopics(str, Enum):
    TEST = "raw.test.event"
