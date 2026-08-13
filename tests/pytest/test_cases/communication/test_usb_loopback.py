import pytest

from tests.pytest.conftest import CTResultRecorder
from tests.pytest.test_interfaces.usb import MockUSBInterface


@pytest.mark.ct(test_id="CT-USB-001", category="communication", interface="USB", equipment="MockHost")
def test_usb_bulk_loopback(usb: MockUSBInterface, ct_result: CTResultRecorder) -> None:
    payload = bytes(range(256))
    assert usb.write(payload) == len(payload)
    assert usb.read() == payload

    transfer = usb.transfers[-1]
    ct_result.metrics.update(
        {
            "bytes_transferred": len(payload),
            "packet_count": transfer.packet_count,
            "max_packet_size": usb.max_packet_size,
            "integrity_error": 0.0,
        }
    )
    ct_result.statistics.update({"endpoint": transfer.endpoint, "transfer_count": len(usb.transfers)})
