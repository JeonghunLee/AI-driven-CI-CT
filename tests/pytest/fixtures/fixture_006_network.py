import pytest

from tests.pytest.test_interfaces.network.mock import MockNetworkInterface


@pytest.fixture
def network() -> MockNetworkInterface:
    interface = MockNetworkInterface()
    interface.connect()
    yield interface
    interface.disconnect()
