import pytest

from tests.pytest.test_equipments.fpga.mock import MockFPGAController
from tests.pytest.test_interfaces.jtag.mock import MockJTAGInterface


@pytest.fixture
def jtag() -> MockJTAGInterface:
    interface = MockJTAGInterface()
    interface.connect()
    yield interface
    interface.disconnect()


@pytest.fixture
def fpga() -> MockFPGAController:
    equipment = MockFPGAController()
    equipment.connect()
    yield equipment
    equipment.disconnect()
