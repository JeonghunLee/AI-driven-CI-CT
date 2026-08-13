from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median, pstdev

from tests.pytest.test_interfaces.uart import MockUARTInterface


@dataclass(frozen=True)
class UARTMeasurement:
    expected_baudrate: int
    samples: tuple[float, ...]
    jitter: float

    @property
    def measured_baudrate(self) -> float:
        return mean(self.samples)

    def metrics(self) -> dict[str, float]:
        measured = self.measured_baudrate
        return {
            "expected_baudrate": self.expected_baudrate,
            "measured_baudrate": round(measured, 3),
            "error": abs(measured - self.expected_baudrate) / self.expected_baudrate,
            "jitter": self.jitter,
        }

    def statistics(self) -> dict[str, float]:
        return {
            "mean": mean(self.samples),
            "median": median(self.samples),
            "min": min(self.samples),
            "max": max(self.samples),
            "stddev": pstdev(self.samples),
        }


class MockSaleaeController:
    def __init__(self, uart: MockUARTInterface, sample_offsets: tuple[int, ...] | None = None) -> None:
        self.uart = uart
        self.sample_offsets = sample_offsets or (-110, -60, -15, 20, 55, 90)
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def measure_uart(self) -> UARTMeasurement:
        if not self.connected:
            raise RuntimeError("Saleae is not connected")
        if not self.uart.transmissions:
            raise RuntimeError("No UART activity was captured")
        expected = self.uart.transmissions[-1].baudrate
        samples = tuple(float(expected + value) for value in self.sample_offsets)
        jitter = (max(samples) - min(samples)) / expected
        return UARTMeasurement(expected, samples, jitter)
