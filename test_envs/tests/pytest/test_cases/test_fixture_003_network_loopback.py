import pytest

from test_envs.tests.pytest.conftest import CTResultRecorder
from test_envs.tests.pytest.fixtures.fixture_003_network import Fixture003, fixture_003


@pytest.mark.ct(
    test_id="CT-NETWORK-001",
    category="communication",
    fixture_id="FIXTURE-003",
    fixture_mode="mock",
    interface="Network",
    equipment="None",
    test_prompt="",
)
def test_network_packet_loopback(fixture_003: Fixture003, ct_result: CTResultRecorder) -> None:
    network = fixture_003.network
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
