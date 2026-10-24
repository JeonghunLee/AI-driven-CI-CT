from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TestInterface(ABC):
    """Transport contract shared by DUT interfaces."""

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def read(self, size: int = -1) -> bytes: ...

    @abstractmethod
    def write(self, data: bytes) -> int: ...

    def execute(self, command: str, **_: Any) -> bytes:
        self.write(command.encode())
        return self.read()

    def __enter__(self) -> "TestInterface":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.disconnect()

