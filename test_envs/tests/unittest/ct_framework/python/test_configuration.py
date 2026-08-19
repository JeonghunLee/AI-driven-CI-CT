from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from test_envs.tools import configuration
from test_envs.tools.configuration import __main__ as configuration_main


class ConfigurationTests(unittest.TestCase):
    def test_project_config_contains_os_and_selected_model(self) -> None:
        value = json.loads(Path("test_envs/configs/config.json").read_text(encoding="utf-8"))
        self.assertIn(value["os"], configuration.SUPPORTED_OS)
        self.assertTrue(value["ollama"]["selected_model"])
        self.assertTrue(value["ollama"]["default_prompt"])
        self.assertGreater(value["ollama"]["max_timeout_s"], 0)
        self.assertGreaterEqual(value["ollama"]["max_retry"], 0)
        self.assertEqual(value["time"]["timezone"], "Asia/Seoul")
        self.assertEqual(value["time"]["utc_offset_hours"], 9)

    def test_configured_time_uses_project_utc_offset(self) -> None:
        with patch(
            "test_envs.tools.configuration.load_config",
            return_value={"time": {"timezone": "Asia/Seoul", "utc_offset_hours": 9}},
        ):
            current = configuration.configured_now()
        self.assertEqual(current.utcoffset().total_seconds(), 9 * 60 * 60)
        self.assertEqual(current.tzname(), "Asia/Seoul")

    def test_set_configured_os_preserves_ollama_config(self) -> None:
        path = Mock()
        directory = Mock()
        source = {"version": 1, "os": "auto", "ollama": {"selected_model": "model:test"}}
        with patch("test_envs.tools.configuration.CONFIG_PATH", path), patch(
            "test_envs.tools.configuration.CONFIG_DIR", directory
        ), patch("test_envs.tools.configuration.load_config", return_value=source), patch(
            "test_envs.tools.configuration.sync_vscode_interpreter"
        ) as sync:
            configuration.set_configured_os("linux")
        written = json.loads(path.write_text.call_args.args[0])
        self.assertEqual(written["os"], "linux")
        self.assertEqual(written["ollama"]["selected_model"], "model:test")
        sync.assert_called_once_with("linux")

    @patch("test_envs.tools.configuration.detected_os", return_value="windows")
    def test_auto_os_uses_windows_venv_interpreter(self, _detected_os) -> None:
        self.assertEqual(
            configuration.vscode_interpreter_path("auto"),
            "${workspaceFolder}/.venv/Scripts/python.exe",
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

    @patch("test_envs.tools.configuration.__main__.os.execv")
    @patch("test_envs.tools.configuration.__main__.sys.argv", ["configuration", "select-os"])
    @patch("test_envs.tools.configuration.__main__.sys._base_executable", "system-python", create=True)
    @patch("test_envs.tools.configuration.__main__.sys.base_prefix", "system-prefix")
    @patch("test_envs.tools.configuration.__main__.sys.prefix", "venv-prefix")
    def test_os_selection_restarts_with_system_python(self, execv) -> None:
        configuration_main._ensure_system_python()
        execv.assert_called_once_with(
            "system-python",
            ["system-python", "-m", "test_envs.tools.configuration", "select-os"],
        )

    @patch("test_envs.tools.configuration.__main__.os.execv")
    @patch("test_envs.tools.configuration.__main__.sys.base_prefix", "system-prefix")
    @patch("test_envs.tools.configuration.__main__.sys.prefix", "system-prefix")
    def test_os_selection_keeps_system_python(self, execv) -> None:
        configuration_main._ensure_system_python()
        execv.assert_not_called()

    @patch("test_envs.tools.configuration._command_version", return_value="ollama version test")
    @patch(
        "test_envs.tools.configuration._ollama_inventory",
        return_value=(True, [{"name": "qwen:test", "size": 42}], None),
    )
    @patch("test_envs.tools.configuration._ollama_executable", return_value="ollama")
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
