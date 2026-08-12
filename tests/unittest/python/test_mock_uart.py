import pytest

from tests.pytest.test_interfaces.uart import MockUARTInterface


def test_uart_loopback_and_lifecycle() -> None:
    uart = MockUARTInterface(baudrate=115_200)
    with uart:
        assert uart.write(b"hello") == 5
        assert uart.read(2) == b"he"
        assert uart.read() == b"llo"
    assert not uart.connected


def test_uart_requires_connection() -> None:
    with pytest.raises(RuntimeError, match="not connected"):
        MockUARTInterface().write(b"x")

