from dataclasses import dataclass
from collections.abc import Iterator

import pytest

from test_envs.tests.pytest.conftest import effective_fixture_mode
from test_envs.tests.pytest.test_equipments.digilent.mock import MockDigilentController
from test_envs.tests.pytest.test_interfaces.usb.mock import MockUSBInterface


@dataclass(frozen=True)
class Fixture002:
    usb: MockUSBInterface
    digilent: MockDigilentController
    mode: str


@pytest.fixture
def fixture_002(request: pytest.FixtureRequest) -> Iterator[Fixture002]:
    mode = effective_fixture_mode(request)
    if mode == "hil":
        pytest.fail(
            "FIXTURE-002 HIL implementation is required in fixture_002_usb_digilent.py",
            pytrace=False,
        )
    usb = MockUSBInterface()
    digilent = MockDigilentController(usb)
    usb.connect()
    digilent.connect()
    try:
        yield Fixture002(usb=usb, digilent=digilent, mode=mode)
    finally:
        digilent.disconnect()
        usb.disconnect()
