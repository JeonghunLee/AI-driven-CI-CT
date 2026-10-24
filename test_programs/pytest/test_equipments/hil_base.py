from __future__ import annotations

from collections.abc import Callable


class HILEquipmentController:
    def __init__(self, connect_handler: Callable[[], None], disconnect_handler: Callable[[], None]) -> None:
        self._connect_handler = connect_handler
        self._disconnect_handler = disconnect_handler
        self.connected = False

    def connect(self) -> None:
        self._connect_handler()
        self.connected = True

    def disconnect(self) -> None:
        if self.connected:
            self._disconnect_handler()
        self.connected = False
