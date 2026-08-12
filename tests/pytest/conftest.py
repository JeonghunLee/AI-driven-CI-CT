import pytest

from tests.pytest.test_equipments.saleae.controller import SaleaeController
from tests.pytest.test_interfaces.uart.interface import UARTInterface


@pytest.fixture
def uart():
    interface = UARTInterface()
    interface.connect()
    yield interface
    interface.disconnect()


@pytest.fixture
def saleae():
    equipment = SaleaeController()
    equipment.connect()
    yield equipment
    equipment.disconnect()
