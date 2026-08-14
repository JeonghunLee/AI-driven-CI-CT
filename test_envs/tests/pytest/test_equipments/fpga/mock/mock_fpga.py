class MockFPGAController:
    def __init__(self) -> None:
        self.connected = False
        self.programmed_image = ""

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def program(self, image: str) -> None:
        if not self.connected:
            raise RuntimeError("FPGA is not connected")
        self.programmed_image = image
