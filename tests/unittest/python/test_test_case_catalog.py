import json
import importlib
import unittest
from pathlib import Path


class TestCaseCatalogTests(unittest.TestCase):
    def test_ct_catalog_registers_uart_usb_and_network(self) -> None:
        value = json.loads(
            Path("tests/pytest/test_cases/catalog.json").read_text(encoding="utf-8")
        )
        entries = {item["test_id"]: item for item in value["test_cases"]}
        self.assertEqual(set(entries), {"CT-UART-001", "CT-USB-001", "CT-NETWORK-001"})
        for entry in entries.values():
            self.assertTrue(Path(entry["module"]).is_file())

    def test_tool_catalogs_register_implemented_tools(self) -> None:
        interface_value = json.loads(
            Path("tests/pytest/test_interfaces/catalog.json").read_text(encoding="utf-8")
        )
        equipment_value = json.loads(
            Path("tests/pytest/test_equipments/catalog.json").read_text(encoding="utf-8")
        )
        interface_ids = {item["tool_id"] for item in interface_value["tools"]}
        equipment_ids = {item["tool_id"] for item in equipment_value["tools"]}
        self.assertEqual(interface_ids, {"uart", "usb", "network", "jtag"})
        self.assertEqual(equipment_ids, {"saleae", "digilent", "fpga"})
        for item in interface_value["tools"] + equipment_value["tools"]:
            self.assertEqual(set(item["implementations"]), {"mock", "hil"})
            for implementation in item["implementations"].values():
                module = importlib.import_module(implementation["module"])
                self.assertTrue(hasattr(module, implementation["class"]))

    def test_test_cases_reference_registered_tools(self) -> None:
        cases = json.loads(
            Path("tests/pytest/test_cases/catalog.json").read_text(encoding="utf-8")
        )["test_cases"]
        interfaces = {
            item["tool_id"]
            for item in json.loads(
                Path("tests/pytest/test_interfaces/catalog.json").read_text(encoding="utf-8")
            )["tools"]
        }
        equipments = {
            item["tool_id"]
            for item in json.loads(
                Path("tests/pytest/test_equipments/catalog.json").read_text(encoding="utf-8")
            )["tools"]
        }
        for case in cases:
            self.assertIn(case["interface_tool"], interfaces)
            self.assertIn(case["test_mode"], {"mock", "hil"})
            self.assertNotIn("interface_mode", case)
            self.assertNotIn("equipment_mode", case)
            if case["equipment_tool"] is not None:
                self.assertIn(case["equipment_tool"], equipments)


if __name__ == "__main__":
    unittest.main()
