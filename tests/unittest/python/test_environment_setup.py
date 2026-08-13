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

    @patch("tools.environment_setup._ollama_ready", return_value=False)
    @patch("tools.environment_setup._ollama_executable", return_value="ollama")
    def test_setup_does_not_start_background_server(self, _executable: Mock, _ready: Mock) -> None:
        with self.assertRaisesRegex(RuntimeError, "Foreground"):
            environment_setup.setup_ollama(platform="auto")


if __name__ == "__main__":
    unittest.main()
