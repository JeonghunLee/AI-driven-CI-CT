import unittest

from test_envs.tests.pytest.test_equipments.digilent import MockDigilentController
from test_envs.tests.pytest.test_interfaces.usb import MockUSBInterface


class MockDigilentTests(unittest.TestCase):
    def test_digilent_measures_usb_transfer(self) -> None:
        usb = MockUSBInterface(max_packet_size=4)
        usb.connect()
        usb.write(b"abcdef")
        equipment = MockDigilentController(usb)
        equipment.connect()
        measurement = equipment.measure_usb()
        self.assertEqual(measurement.bytes_transferred, 6)
        self.assertEqual(measurement.packet_count, 2)
        self.assertEqual(measurement.bus_voltage, 5.0)

    def test_digilent_requires_connection(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not connected"):
            MockDigilentController(MockUSBInterface()).measure_usb()


if __name__ == "__main__":
    unittest.main()
