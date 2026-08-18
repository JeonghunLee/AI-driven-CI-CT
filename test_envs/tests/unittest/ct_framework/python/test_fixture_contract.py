import importlib
import unittest
from pathlib import Path
from types import SimpleNamespace

from test_envs.tests.pytest.conftest import effective_fixture_mode


TEST_MODULES = (
    "test_envs.tests.pytest.test_cases.test_fixture_001_uart_timing",
    "test_envs.tests.pytest.test_cases.test_fixture_002_usb_loopback",
    "test_envs.tests.pytest.test_cases.test_fixture_003_network_loopback",
)


class FixtureContractTests(unittest.TestCase):
    def test_cli_fixture_mode_overrides_marker(self) -> None:
        marker = SimpleNamespace(kwargs={"fixture_mode": "mock"})
        request = SimpleNamespace(
            config=SimpleNamespace(getoption=lambda name: "hil"),
            node=SimpleNamespace(get_closest_marker=lambda name: marker),
        )
        self.assertEqual(effective_fixture_mode(request), "hil")

    def test_marker_fixture_mode_is_default(self) -> None:
        marker = SimpleNamespace(kwargs={"fixture_mode": "mock"})
        request = SimpleNamespace(
            config=SimpleNamespace(getoption=lambda name: "marker"),
            node=SimpleNamespace(get_closest_marker=lambda name: marker),
        )
        self.assertEqual(effective_fixture_mode(request), "mock")

    def test_ct_markers_define_fixture_selection(self) -> None:
        test_ids: set[str] = set()
        fixture_ids: set[str] = set()
        for module_name in TEST_MODULES:
            module = importlib.import_module(module_name)
            test_functions = [
                value
                for name, value in vars(module).items()
                if name.startswith("test_") and callable(value)
            ]
            self.assertEqual(len(test_functions), 1)
            markers = getattr(test_functions[0], "pytestmark", [])
            marker = next(item for item in markers if item.name == "ct")
            self.assertEqual(marker.kwargs["fixture_mode"], "mock")
            self.assertIn(marker.kwargs["category"], {"communication", "timing"})
            test_ids.add(marker.kwargs["test_id"])
            fixture_ids.add(marker.kwargs["fixture_id"])

        self.assertEqual(test_ids, {"CT-UART-001", "CT-USB-001", "CT-NETWORK-001"})
        self.assertEqual(fixture_ids, {"FIXTURE-001", "FIXTURE-002", "FIXTURE-003"})

    def test_test_cases_import_pytest_fixtures(self) -> None:
        expected = {
            TEST_MODULES[0]: {"fixture_001"},
            TEST_MODULES[1]: {"fixture_002"},
            TEST_MODULES[2]: {"fixture_003"},
        }
        for module_name, fixture_names in expected.items():
            module = importlib.import_module(module_name)
            for fixture_name in fixture_names:
                fixture = getattr(module, fixture_name)
                self.assertIsNotNone(getattr(fixture, "_fixture_function_marker", None))

    def test_catalog_files_are_not_used(self) -> None:
        self.assertFalse(Path("test_envs/configs/pytest").exists())

    def test_mock_implementations_remain_available(self) -> None:
        modules_and_classes = {
            "test_envs.tests.pytest.test_interfaces.uart": "MockUARTInterface",
            "test_envs.tests.pytest.test_interfaces.usb": "MockUSBInterface",
            "test_envs.tests.pytest.test_interfaces.network": "MockNetworkInterface",
            "test_envs.tests.pytest.test_interfaces.jtag": "MockJTAGInterface",
            "test_envs.tests.pytest.test_equipments.saleae": "MockSaleaeController",
            "test_envs.tests.pytest.test_equipments.digilent": "MockDigilentController",
            "test_envs.tests.pytest.test_equipments.fpga": "MockFPGAController",
        }
        for module_name, class_name in modules_and_classes.items():
            self.assertTrue(hasattr(importlib.import_module(module_name), class_name))


if __name__ == "__main__":
    unittest.main()
