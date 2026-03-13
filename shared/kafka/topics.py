"""Shared topic-name constants and an Enum of all topics.

Keep module-level string constants for backward compatibility and also
export a `KafkaTopics` enum for clearer usage in code.
"""

from __future__ import annotations

from enum import Enum


class KafkaTopics(str, Enum):
    TEST = "raw.test.event"
    CMD_FEATURE_COLLECTION = "cmd.feature_collection"
    CMD_MODEL_TRAINING = "cmd.model_training"
    RAW_ENERGY_CHARTS = "raw.energy_charts"
    FEATURES_ENERGY_CHARTS = "features.energy_charts"
    FEATURES_ENERGY_CHARTS_UPDATED = "features.energy_charts.updated"
