import unittest

from tests.pytest.test_interfaces.usb import MockUSBInterface


class MockUSBTests(unittest.TestCase):
    def test_usb_packetized_loopback(self) -> None:
        usb = MockUSBInterface(max_packet_size=4)
        with usb:
            self.assertEqual(usb.write(b"abcdef"), 6)
            self.assertEqual(usb.read(), b"abcdef")
            self.assertEqual(usb.transfers[-1].packet_count, 2)

    def test_usb_requires_connection(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not connected"):
            MockUSBInterface().write(b"x")


if __name__ == "__main__":
    unittest.main()
