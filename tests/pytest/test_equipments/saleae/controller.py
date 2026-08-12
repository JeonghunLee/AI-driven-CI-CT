class SaleaeController:
    def __init__(self, measured_baudrate: int = 921502, jitter: float = 0.018):
        self.measured_baudrate = measured_baudrate
        self.jitter = jitter
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def capture_uart_metrics(self) -> dict:
        if not self.connected:
            raise RuntimeError("Saleae not connected")
        return {
            "expected_baudrate": 921600,
            "measured_baudrate": self.measured_baudrate,
            "error": abs(self.measured_baudrate - 921600) / 921600,
            "jitter": self.jitter,
        }
