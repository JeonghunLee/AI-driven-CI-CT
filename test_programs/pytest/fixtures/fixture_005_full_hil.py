import os
from dataclasses import dataclass

import pytest

FIXTURE_META = {
    "fixture_id": "FIXTURE-005",
    "interfaces": [],
    "equipments": [],
    "modes": {
        "mock": {"enabled": False},
        "hil": {"enabled": True},
    },
}


@dataclass(frozen=True)
class FullHILContext:
    test_mode: str = "hil"
    enabled: bool = True


@pytest.fixture
def full_hil() -> FullHILContext:
    if os.getenv("CICT_HIL") != "1":
        pytest.skip("CICT_HIL=1 is required")
    return FullHILContext()
