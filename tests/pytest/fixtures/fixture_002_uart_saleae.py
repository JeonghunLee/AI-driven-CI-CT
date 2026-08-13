import pytest

from tests.pytest.test_equipments.saleae.mock import MockSaleaeController
from tests.pytest.test_interfaces.uart.mock import MockUARTInterface


@pytest.fixture
def saleae(uart: MockUARTInterface) -> MockSaleaeController:
    equipment = MockSaleaeController(uart)
    equipment.connect()
    yield equipment
    equipment.disconnect()
