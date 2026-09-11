import importlib
import unittest
from pathlib import Path
from types import SimpleNamespace

from test_envs.tests.pytest.conftest import effective_fixture_mode, fixture_registry
from test_envs.tools.test_catalog import catalog_tests


TEST_MODULES = tuple(
    ".".join(Path(test["test_path"]).with_suffix("").parts)
    for test in catalog_tests()
)


class FixtureContractTests(unittest.TestCase):
    def test_cli_fixture_mode_overrides_marker(self) -> None:
        marker = SimpleNamespace(kwargs={"fixture_id": "FIXTURE-001", "fixture_mode": "mock"})
        request = SimpleNamespace(
            config=SimpleNamespace(getoption=lambda name: "hil"),
            node=SimpleNamespace(get_closest_marker=lambda name: marker),
        )
        self.assertEqual(effective_fixture_mode(request), "hil")

    def test_marker_fixture_mode_is_default(self) -> None:
        marker = SimpleNamespace(kwargs={"fixture_id": "FIXTURE-001", "fixture_mode": "mock"})
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
            self.assertNotIn("interface", marker.kwargs)
            self.assertNotIn("equipment", marker.kwargs)
            self.assertIn("test_prompt", marker.kwargs)
            test_ids.add(marker.kwargs["test_id"])
            fixture_ids.add(marker.kwargs["fixture_id"])

        self.assertEqual(test_ids, {test["test_id"] for test in catalog_tests()})
        self.assertEqual(fixture_ids, {test["fixture_id"] for test in catalog_tests()})

    def test_fixture_meta_defines_tools_and_modes(self) -> None:
        registry = fixture_registry()
        self.assertEqual(registry["FIXTURE-001"]["interfaces"], ["UART"])
        self.assertEqual(registry["FIXTURE-001"]["equipments"], ["Saleae"])
        self.assertEqual(registry["FIXTURE-002"]["interfaces"], ["USB"])
        self.assertEqual(registry["FIXTURE-002"]["equipments"], ["Digilent"])
        self.assertEqual(registry["FIXTURE-003"]["interfaces"], ["Network"])
        self.assertEqual(registry["FIXTURE-003"]["equipments"], [])
        for meta in registry.values():
            self.assertIsInstance(meta["modes"]["mock"]["enabled"], bool)
            self.assertIsInstance(meta["modes"]["hil"]["enabled"], bool)

    def test_test_cases_import_pytest_fixtures(self) -> None:
        expected = {
            module_name: {test["fixture_id"].lower().replace("-", "_")}
            for module_name, test in zip(TEST_MODULES, catalog_tests())
        }
        for module_name, fixture_names in expected.items():
            module = importlib.import_module(module_name)
            for fixture_name in fixture_names:
                fixture = getattr(module, fixture_name)
                self.assertIsNotNone(getattr(fixture, "_fixture_function_marker", None))

    def test_legacy_config_catalog_is_not_used(self) -> None:
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
