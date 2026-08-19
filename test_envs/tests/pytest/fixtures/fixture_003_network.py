from dataclasses import dataclass
from collections.abc import Iterator

import pytest

from test_envs.tests.pytest.conftest import effective_fixture_mode
from test_envs.tests.pytest.test_interfaces.network.mock import MockNetworkInterface

FIXTURE_META = {
    "fixture_id": "FIXTURE-003",
    "interfaces": ["Network"],
    "equipments": [],
    "modes": {
        "mock": {"enabled": True},
        "hil": {"enabled": True},
    },
}


@dataclass(frozen=True)
class Fixture003:
    network: MockNetworkInterface
    mode: str


@pytest.fixture
def fixture_003(request: pytest.FixtureRequest) -> Iterator[Fixture003]:
    mode = effective_fixture_mode(request)
    if mode == "hil":
        pytest.fail(
            "FIXTURE-003 HIL implementation is required in fixture_003_network.py",
            pytrace=False,
        )
    network = MockNetworkInterface()
    network.connect()
    try:
        yield Fixture003(network=network, mode=mode)
    finally:
        network.disconnect()
