import pytest

from tests.pytest.conftest import CTResultRecorder
from tests.pytest.test_interfaces.network import MockNetworkInterface


@pytest.mark.ct(
    test_id="CT-NETWORK-001",
    category="communication",
    interface="Network",
    equipment="MockHost",
)
def test_network_packet_loopback(network: MockNetworkInterface, ct_result: CTResultRecorder) -> None:
    payload = b'{"command":"health","sequence":1}'
    assert network.write(payload) == len(payload)
    assert network.read() == payload

    packet = network.packets[-1]
    ct_result.metrics.update(
        {
            "bytes_transferred": len(payload),
            "packet_count": len(network.packets),
            "latency_ms": packet.latency_ms,
            "integrity_error": 0.0,
        }
    )
    ct_result.statistics.update({"host": packet.host, "port": packet.port})
