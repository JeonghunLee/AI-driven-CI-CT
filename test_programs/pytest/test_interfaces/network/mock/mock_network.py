from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from ...base import TestInterface


@dataclass(frozen=True)
class NetworkPacket:
    host: str
    port: int
    data: bytes
    latency_ms: float


class MockNetworkInterface(TestInterface):
    def __init__(self, host: str = "127.0.0.1", port: int = 9000, latency_ms: float = 1.25) -> None:
        if not host:
            raise ValueError("host is required")
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        self.host = host
        self.port = port
        self.latency_ms = latency_ms
        self.connected = False
        self.packets: list[NetworkPacket] = []
        self._rx: deque[int] = deque()

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False
        self._rx.clear()

    def write(self, data: bytes) -> int:
        if not self.connected:
            raise RuntimeError("Network is not connected")
        payload = bytes(data)
        self.packets.append(NetworkPacket(self.host, self.port, payload, self.latency_ms))
        self._rx.extend(payload)
        return len(payload)

    def read(self, size: int = -1) -> bytes:
        if not self.connected:
            raise RuntimeError("Network is not connected")
        count = len(self._rx) if size < 0 else min(size, len(self._rx))
        return bytes(self._rx.popleft() for _ in range(count))
