from __future__ import annotations

from collections.abc import Callable

from .base import TestInterface


class HILTransportInterface(TestInterface):
    def __init__(
        self,
        connect_handler: Callable[[], None],
        disconnect_handler: Callable[[], None],
        read_handler: Callable[[int], bytes],
        write_handler: Callable[[bytes], int],
    ) -> None:
        self._connect_handler = connect_handler
        self._disconnect_handler = disconnect_handler
        self._read_handler = read_handler
        self._write_handler = write_handler
        self.connected = False

    def connect(self) -> None:
        self._connect_handler()
        self.connected = True

    def disconnect(self) -> None:
        if self.connected:
            self._disconnect_handler()
        self.connected = False

    def read(self, size: int = -1) -> bytes:
        if not self.connected:
            raise RuntimeError("HIL interface is not connected")
        return bytes(self._read_handler(size))

    def write(self, data: bytes) -> int:
        if not self.connected:
            raise RuntimeError("HIL interface is not connected")
        return int(self._write_handler(bytes(data)))
