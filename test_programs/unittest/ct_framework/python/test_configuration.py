from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from test_envs.tools import configuration
from test_envs.tools.configuration import __main__ as configuration_main


class ConfigurationTests(unittest.TestCase):
    def test_project_config_is_split_by_environment_and_ollama(self) -> None:
        env = json.loads(Path("test_envs/configs/config_env.json").read_text(encoding="utf-8"))
        ollama = json.loads(Path("test_envs/configs/config_ollama.json").read_text(encoding="utf-8"))
        self.assertIn(env["os"], configuration.SUPPORTED_OS)
        self.assertTrue(ollama["selected_model"])
        self.assertTrue(ollama["default_prompt"])
        self.assertGreater(ollama["max_timeout_s"], 0)
        self.assertGreaterEqual(ollama["max_retry"], 0)
        self.assertEqual(env["time"]["timezone"], "Asia/Seoul")
        self.assertEqual(env["time"]["utc_offset_hours"], 9)

    def test_configured_time_uses_project_utc_offset(self) -> None:
        with patch(
            "test_envs.tools.configuration.load_config",
            return_value={"time": {"timezone": "Asia/Seoul", "utc_offset_hours": 9}},
        ):
            current = configuration.configured_now()
        self.assertEqual(current.utcoffset().total_seconds(), 9 * 60 * 60)
        self.assertEqual(current.tzname(), "Asia/Seoul")

    def test_set_configured_os_updates_only_environment_config(self) -> None:
        path = Mock()
        directory = Mock()
        source = {"version": 1, "os": "auto", "time": {"timezone": "Asia/Seoul", "utc_offset_hours": 9}}
        with patch("test_envs.tools.configuration.ENV_CONFIG_PATH", path), patch(
            "test_envs.tools.configuration.CONFIG_DIR", directory
        ), patch("test_envs.tools.configuration.load_env_config", return_value=source), patch(
            "test_envs.tools.configuration.sync_vscode_interpreter"
        ) as sync:
            configuration.set_configured_os("linux")
        written = json.loads(path.write_text.call_args.args[0])
        self.assertEqual(written["os"], "linux")
        self.assertEqual(written["time"]["timezone"], "Asia/Seoul")
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
    def test_split_checks_contain_required_environment_state(
        self, _executable, _inventory, _version
    ) -> None:
        envs = configuration.build_envs_check()
        ollama = configuration.build_ollama_check()
        self.assertIn("configured", envs["os"])
        self.assertIn("detected", envs["os"])
        self.assertTrue(envs["python"]["installed"])
        self.assertTrue(ollama["ollama"]["installed"])
        self.assertEqual(ollama["ollama"]["supported_models"][0]["name"], "qwen:test")

    def test_combined_check_remains_available_to_runtime_consumers(self) -> None:
        value = configuration.build_check()
        self.assertIn("python", value)
        self.assertIn("ollama", value)

    def test_combined_config_remains_available_to_runtime_consumers(self) -> None:
        value = configuration.load_config()
        self.assertIn("os", value)
        self.assertIn("ollama", value)


if __name__ == "__main__":
    unittest.main()
