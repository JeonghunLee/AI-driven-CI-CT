from dataclasses import dataclass
from collections.abc import Iterator

import pytest

from test_envs.tests.pytest.conftest import effective_fixture_mode
from test_envs.tests.pytest.test_equipments.saleae.mock import MockSaleaeController
from test_envs.tests.pytest.test_interfaces.uart.mock import MockUARTInterface


@dataclass(frozen=True)
class Fixture001:
    uart: MockUARTInterface
    saleae: MockSaleaeController
    mode: str


@pytest.fixture
def fixture_001(request: pytest.FixtureRequest) -> Iterator[Fixture001]:
    mode = effective_fixture_mode(request)
    if mode == "hil":
        pytest.fail(
            "FIXTURE-001 HIL implementation is required in fixture_001_uart_saleae.py",
            pytrace=False,
        )
    uart = MockUARTInterface()
    saleae = MockSaleaeController(uart)
    uart.connect()
    saleae.connect()
    try:
        yield Fixture001(uart=uart, saleae=saleae, mode=mode)
    finally:
        saleae.disconnect()
        uart.disconnect()
