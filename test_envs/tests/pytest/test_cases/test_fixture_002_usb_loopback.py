import pytest

from test_envs.tests.pytest.conftest import CTResultRecorder
from test_envs.tests.pytest.fixtures.fixture_002_usb_digilent import Fixture002, fixture_002


@pytest.mark.ct(
    test_id="CT-USB-001",
    category="communication",
    fixture_id="FIXTURE-002",
    fixture_mode="mock",
    test_prompt="",
)
def test_usb_bulk_loopback(
    fixture_002: Fixture002,
    ct_result: CTResultRecorder,
) -> None:
    usb = fixture_002.usb
    digilent = fixture_002.digilent
    payload = bytes(range(256))
    assert usb.write(payload) == len(payload)
    assert usb.read() == payload

    measurement = digilent.measure_usb()
    ct_result.metrics.update(measurement.metrics())
    ct_result.statistics.update({"endpoint": usb.transfers[-1].endpoint, "transfer_count": len(usb.transfers)})
