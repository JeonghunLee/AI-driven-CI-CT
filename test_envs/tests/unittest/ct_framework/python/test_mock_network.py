import unittest

from test_envs.tests.pytest.test_interfaces.network import MockNetworkInterface


class MockNetworkTests(unittest.TestCase):
    def test_network_packet_loopback(self) -> None:
        network = MockNetworkInterface(port=8080, latency_ms=2.5)
        with network:
            self.assertEqual(network.write(b"ping"), 4)
            self.assertEqual(network.read(), b"ping")
            self.assertEqual(network.packets[-1].latency_ms, 2.5)

    def test_network_validates_port(self) -> None:
        with self.assertRaisesRegex(ValueError, "port"):
            MockNetworkInterface(port=0)


if __name__ == "__main__":
    unittest.main()
