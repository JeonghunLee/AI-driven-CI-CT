from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tools import configuration


class ConfigurationTests(unittest.TestCase):
    def test_project_config_contains_os_and_selected_model(self) -> None:
        value = json.loads(Path("config/config.json").read_text(encoding="utf-8"))
        self.assertIn(value["os"], configuration.SUPPORTED_OS)
        self.assertTrue(value["ollama"]["selected_model"])

    def test_set_configured_os_preserves_ollama_config(self) -> None:
        path = Mock()
        directory = Mock()
        source = {"version": 1, "os": "auto", "ollama": {"selected_model": "model:test"}}
        with patch("tools.configuration.CONFIG_PATH", path), patch(
            "tools.configuration.CONFIG_DIR", directory
        ), patch("tools.configuration.load_config", return_value=source), patch(
            "tools.configuration.sync_vscode_interpreter"
        ) as sync:
            configuration.set_configured_os("linux")
        written = json.loads(path.write_text.call_args.args[0])
        self.assertEqual(written["os"], "linux")
        self.assertEqual(written["ollama"]["selected_model"], "model:test")
        sync.assert_called_once_with("linux")

    @patch("tools.configuration.detected_os", return_value="windows")
    def test_auto_os_uses_windows_venv_interpreter(self, _detected_os) -> None:
        self.assertEqual(
            configuration.vscode_interpreter_path("auto"),
            "${workspaceFolder}\\.venv\\Scripts\\python.exe",
        )

    def test_unix_hosts_use_bin_python(self) -> None:
        self.assertEqual(
            configuration.vscode_interpreter_path("linux"),
            "${workspaceFolder}/.venv/bin/python",
        )
        self.assertEqual(
            configuration.vscode_interpreter_path("macos"),
            "${workspaceFolder}/.venv/bin/python",
        )

    @patch("tools.configuration._command_version", return_value="ollama version test")
    @patch(
        "tools.configuration._ollama_inventory",
        return_value=(True, [{"name": "qwen:test", "size": 42}], None),
    )
    @patch("tools.configuration._ollama_executable", return_value="ollama")
    def test_check_contains_required_environment_state(
        self, _executable, _inventory, _version
    ) -> None:
        value = configuration.build_check()
        self.assertIn("configured", value["os"])
        self.assertIn("detected", value["os"])
        self.assertTrue(value["python"]["installed"])
        self.assertTrue(value["ollama"]["installed"])
        self.assertEqual(value["ollama"]["supported_models"][0]["name"], "qwen:test")


if __name__ == "__main__":
    unittest.main()
