from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import monotonic

from ..base import TestInterface


@dataclass(frozen=True)
class Transmission:
    timestamp: float
    data: bytes
    baudrate: int


class MockUARTInterface(TestInterface):
    """Deterministic UART loopback used when no DUT is connected."""

    def __init__(self, port: str = "MOCK", baudrate: int = 921_600) -> None:
        if baudrate <= 0:
            raise ValueError("baudrate must be positive")
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        self.transmissions: list[Transmission] = []
        self._rx: deque[int] = deque()

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False
        self._rx.clear()

    def write(self, data: bytes) -> int:
        if not self.connected:
            raise RuntimeError("UART is not connected")
        payload = bytes(data)
        self.transmissions.append(Transmission(monotonic(), payload, self.baudrate))
        self._rx.extend(payload)
        return len(payload)

    def read(self, size: int = -1) -> bytes:
        if not self.connected:
            raise RuntimeError("UART is not connected")
        count = len(self._rx) if size < 0 else min(size, len(self._rx))
        return bytes(self._rx.popleft() for _ in range(count))

