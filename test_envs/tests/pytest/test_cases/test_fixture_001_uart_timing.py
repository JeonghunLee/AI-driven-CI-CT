import pytest

from test_envs.tests.pytest.conftest import CTResultRecorder
from test_envs.tests.pytest.test_equipments.saleae import MockSaleaeController
from test_envs.tests.pytest.test_interfaces.uart import MockUARTInterface


@pytest.mark.ct(
    test_id="CT-UART-001",
    category="timing",
    interface="UART",
    equipment="Saleae",
)
def test_uart_timing(
    uart: MockUARTInterface, saleae: MockSaleaeController, ct_result: CTResultRecorder
) -> None:
    uart.write(b"CI/CT timing probe")
    assert uart.read() == b"CI/CT timing probe"

    measurement = saleae.measure_uart()
    metrics = measurement.metrics()
    ct_result.metrics.update(metrics)
    ct_result.statistics.update(measurement.statistics())
    assert metrics["error"] < 0.02
    assert metrics["jitter"] < 0.02
