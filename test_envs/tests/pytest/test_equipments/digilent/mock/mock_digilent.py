from __future__ import annotations

from dataclasses import dataclass

from test_envs.tests.pytest.test_interfaces.usb import MockUSBInterface


@dataclass(frozen=True)
class DigilentUSBMeasurement:
    bytes_transferred: int
    packet_count: int
    max_packet_size: int
    bus_voltage: float

    def metrics(self) -> dict[str, float | int]:
        return {
            "bytes_transferred": self.bytes_transferred,
            "packet_count": self.packet_count,
            "max_packet_size": self.max_packet_size,
            "bus_voltage": self.bus_voltage,
            "integrity_error": 0.0,
        }


class MockDigilentController:
    def __init__(self, usb: MockUSBInterface, bus_voltage: float = 5.0) -> None:
        if bus_voltage <= 0:
            raise ValueError("bus_voltage must be positive")
        self.usb = usb
        self.bus_voltage = bus_voltage
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def measure_usb(self) -> DigilentUSBMeasurement:
        if not self.connected:
            raise RuntimeError("Digilent is not connected")
        if not self.usb.transfers:
            raise RuntimeError("No USB activity was captured")
        transfer = self.usb.transfers[-1]
        return DigilentUSBMeasurement(
            bytes_transferred=len(transfer.data),
            packet_count=transfer.packet_count,
            max_packet_size=self.usb.max_packet_size,
            bus_voltage=self.bus_voltage,
        )
