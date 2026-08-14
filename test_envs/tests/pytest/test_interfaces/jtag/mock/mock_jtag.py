from collections import deque

from ...base import TestInterface


class MockJTAGInterface(TestInterface):
    def __init__(self) -> None:
        self.connected = False
        self._rx: deque[int] = deque()

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False
        self._rx.clear()

    def write(self, data: bytes) -> int:
        if not self.connected:
            raise RuntimeError("JTAG is not connected")
        payload = bytes(data)
        self._rx.extend(payload)
        return len(payload)

    def read(self, size: int = -1) -> bytes:
        if not self.connected:
            raise RuntimeError("JTAG is not connected")
        count = len(self._rx) if size < 0 else min(size, len(self._rx))
        return bytes(self._rx.popleft() for _ in range(count))
