class UARTInterface:
    """Loopback mock for CT scaffolding: reads return the most recent write."""

    def __init__(self, baudrate: int = 921600):
        self.baudrate = baudrate
        self.connected = False
        self._buffer = []

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def write(self, data: str) -> None:
        if not self.connected:
            raise RuntimeError("UART not connected")
        self._buffer.append(data)

    def read(self) -> str:
        if not self.connected:
            raise RuntimeError("UART not connected")
        return self._buffer[-1] if self._buffer else ""
