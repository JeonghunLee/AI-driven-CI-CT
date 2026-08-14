import pytest

from test_envs.tests.pytest.test_equipments.digilent.mock import MockDigilentController
from test_envs.tests.pytest.test_interfaces.usb.mock import MockUSBInterface


@pytest.fixture
def usb() -> MockUSBInterface:
    interface = MockUSBInterface()
    interface.connect()
    yield interface
    interface.disconnect()


@pytest.fixture
def digilent(usb: MockUSBInterface) -> MockDigilentController:
    equipment = MockDigilentController(usb)
    equipment.connect()
    yield equipment
    equipment.disconnect()
