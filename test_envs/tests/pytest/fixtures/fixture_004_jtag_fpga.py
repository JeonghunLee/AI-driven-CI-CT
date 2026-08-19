import pytest

from test_envs.tests.pytest.test_equipments.fpga.mock import MockFPGAController
from test_envs.tests.pytest.test_interfaces.jtag.mock import MockJTAGInterface

FIXTURE_META = {
    "fixture_id": "FIXTURE-004",
    "interfaces": ["JTAG"],
    "equipments": ["FPGA"],
    "modes": {
        "mock": {"enabled": True},
        "hil": {"enabled": False},
    },
}


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
