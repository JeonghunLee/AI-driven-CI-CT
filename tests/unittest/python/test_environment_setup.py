from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from tools import environment_setup


class OllamaServerLifecycleTests(unittest.TestCase):
    @patch("tools.environment_setup.sys.platform", "win32")
    def test_auto_platform_detects_windows(self) -> None:
        self.assertEqual(environment_setup.selected_platform("auto"), "windows")

    @patch("tools.environment_setup.sys.platform", "darwin")
    def test_auto_platform_detects_macos(self) -> None:
        self.assertEqual(environment_setup.selected_platform("auto"), "macos")

    @patch("tools.environment_setup.sys.platform", "linux")
    def test_auto_platform_detects_linux(self) -> None:
        self.assertEqual(environment_setup.selected_platform("auto"), "linux")

    @patch("tools.environment_setup.sys.platform", "linux")
    def test_cross_platform_selection_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "does not match host"):
            environment_setup.selected_platform("windows")

    @patch("tools.environment_setup.configured_os", return_value="linux")
    @patch("tools.environment_setup.sys.platform", "linux")
    def test_config_platform_uses_project_config(self, _configured_os: Mock) -> None:
        self.assertEqual(environment_setup.selected_platform("config"), "linux")

    @patch("tools.environment_setup.subprocess.Popen")
    @patch("tools.environment_setup._ollama_ready", return_value=True)
    def test_existing_server_is_not_started_or_stopped(self, _ready: Mock, popen: Mock) -> None:
        with environment_setup._ollama_server("ollama", "http://127.0.0.1:11434"):
            pass

        popen.assert_not_called()

    @patch("tools.environment_setup.time.sleep")
    @patch("tools.environment_setup._ollama_ready", side_effect=[False, True])
    @patch("tools.environment_setup.subprocess.Popen")
    def test_setup_owned_server_is_stopped(
        self, popen: Mock, _ready: Mock, _sleep: Mock
    ) -> None:
        process = popen.return_value
        process.poll.return_value = None

        with environment_setup._ollama_server("ollama", "http://127.0.0.1:11434"):
            pass

        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=10)

    @patch("tools.environment_setup.time.sleep")
    @patch("tools.environment_setup._ollama_ready", side_effect=[False, True])
    @patch("tools.environment_setup.subprocess.Popen")
    def test_setup_owned_server_is_stopped_after_failure(
        self, popen: Mock, _ready: Mock, _sleep: Mock
    ) -> None:
        process = popen.return_value
        process.poll.return_value = None

        with self.assertRaisesRegex(RuntimeError, "pull failed"):
            with environment_setup._ollama_server("ollama", "http://127.0.0.1:11434"):
                raise RuntimeError("pull failed")

        process.terminate.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
