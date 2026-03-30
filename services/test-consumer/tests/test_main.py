from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_main_module() -> ModuleType:
    module_path = Path(__file__).resolve().parents[1] / "src" / "main.py"
    spec = importlib.util.spec_from_file_location("test_consumer_main", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_topic_name_defaults_to_test_topic(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_main_module()
    monkeypatch.delenv("KAFKA_TOPIC", raising=False)
    assert module._topic_name() == "raw.test.event"


def test_topic_name_uses_explicit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_main_module()
    monkeypatch.setenv("KAFKA_TOPIC", "custom.topic")
    assert module._topic_name() == "custom.topic"
