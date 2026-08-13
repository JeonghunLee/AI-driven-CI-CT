from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from ..base import TestInterface


@dataclass(frozen=True)
class USBTransfer:
    endpoint: int
    data: bytes
    packet_count: int


class MockUSBInterface(TestInterface):
    def __init__(self, endpoint: int = 1, max_packet_size: int = 64) -> None:
        if endpoint <= 0:
            raise ValueError("endpoint must be positive")
        if max_packet_size <= 0:
            raise ValueError("max_packet_size must be positive")
        self.endpoint = endpoint
        self.max_packet_size = max_packet_size
        self.connected = False
        self.transfers: list[USBTransfer] = []
        self._rx: deque[int] = deque()

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False
        self._rx.clear()

    def write(self, data: bytes) -> int:
        if not self.connected:
            raise RuntimeError("USB is not connected")
        payload = bytes(data)
        packets = (len(payload) + self.max_packet_size - 1) // self.max_packet_size
        self.transfers.append(USBTransfer(self.endpoint, payload, packets))
        self._rx.extend(payload)
        return len(payload)

    def read(self, size: int = -1) -> bytes:
        if not self.connected:
            raise RuntimeError("USB is not connected")
        count = len(self._rx) if size < 0 else min(size, len(self._rx))
        return bytes(self._rx.popleft() for _ in range(count))
