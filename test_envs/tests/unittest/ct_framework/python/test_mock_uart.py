import unittest

from test_envs.tests.pytest.test_interfaces.uart import MockUARTInterface


class MockUARTTests(unittest.TestCase):
    def test_uart_loopback_and_lifecycle(self) -> None:
        uart = MockUARTInterface(baudrate=115_200)
        with uart:
            self.assertEqual(uart.write(b"hello"), 5)
            self.assertEqual(uart.read(2), b"he")
            self.assertEqual(uart.read(), b"llo")
        self.assertFalse(uart.connected)

    def test_uart_requires_connection(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not connected"):
            MockUARTInterface().write(b"x")


if __name__ == "__main__":
    unittest.main()
