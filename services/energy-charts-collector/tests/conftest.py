import json
import sys
from pathlib import Path

import pytest

# Ensure the local `src/` directory is on sys.path so tests can import the
# package without installing it into the environment.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def public_power_sample() -> dict:
    p = Path(__file__).parent / "fixtures" / "public_power_sample.json"
    return json.loads(p.read_text())
