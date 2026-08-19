import pytest

from test_envs.tests.pytest.conftest import CTResultRecorder
from test_envs.tests.pytest.fixtures.fixture_001_uart_saleae import Fixture001, fixture_001


@pytest.mark.ct(
    test_id="CT-UART-001",
    category="timing",
    fixture_id="FIXTURE-001",
    fixture_mode="mock",
    test_prompt="",
)
def test_uart_timing(
    fixture_001: Fixture001, ct_result: CTResultRecorder
) -> None:
    uart = fixture_001.uart
    saleae = fixture_001.saleae
    uart.write(b"CI/CT timing probe")
    assert uart.read() == b"CI/CT timing probe"

    measurement = saleae.measure_uart()
    metrics = measurement.metrics()
    ct_result.metrics.update(metrics)
    ct_result.statistics.update(measurement.statistics())
    assert metrics["error"] < 0.02
    assert metrics["jitter"] < 0.02
