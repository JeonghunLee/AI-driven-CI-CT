import pytest

from tests.pytest.test_interfaces.uart.mock import MockUARTInterface


@pytest.fixture
def uart() -> MockUARTInterface:
    interface = MockUARTInterface()
    interface.connect()
    yield interface
    interface.disconnect()
