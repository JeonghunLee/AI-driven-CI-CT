import pytest

from test_envs.tests.pytest.conftest import CTResultRecorder
from test_envs.tests.pytest.test_interfaces.usb import MockUSBInterface
from test_envs.tests.pytest.test_equipments.digilent import MockDigilentController


@pytest.mark.ct(
    test_id="CT-USB-001",
    category="communication",
    interface="USB",
    equipment="Digilent",
)
def test_usb_bulk_loopback(
    usb: MockUSBInterface,
    digilent: MockDigilentController,
    ct_result: CTResultRecorder,
) -> None:
    payload = bytes(range(256))
    assert usb.write(payload) == len(payload)
    assert usb.read() == payload

    measurement = digilent.measure_usb()
    ct_result.metrics.update(measurement.metrics())
    ct_result.statistics.update({"endpoint": usb.transfers[-1].endpoint, "transfer_count": len(usb.transfers)})
