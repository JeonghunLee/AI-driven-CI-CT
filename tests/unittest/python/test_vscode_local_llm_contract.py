import json
import unittest
from pathlib import Path


class VSCodeLocalLLMContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launch = json.loads(Path(".vscode/launch.json").read_text(encoding="utf-8"))
        self.tasks = json.loads(Path(".vscode/tasks.json").read_text(encoding="utf-8"))
        self.config = json.loads(Path("config/config.json").read_text(encoding="utf-8"))

    def test_selected_preset_has_model_name(self) -> None:
        self.assertIn(self.config["os"], ["auto", "windows", "linux", "macos"])
        self.assertTrue(self.config["ollama"]["selected_model"])

    def test_launch_setup_uses_internal_model_config(self) -> None:
        setup = next(
            item for item in self.launch["configurations"]
            if item["name"] == "Setup 2: Install Ollama and Local LLM"
        )
        self.assertEqual(
            setup["args"],
            ["ollama", "--platform", "${input:setupPlatform}"],
        )
        self.assertTrue(any("Check File" in item["name"] for item in self.launch["configurations"]))

    def test_python_setup_uses_platform_picker(self) -> None:
        launch = next(
            item for item in self.launch["configurations"]
            if item["name"] == "Setup 1: Install Python Virtual Environment"
        )
        task = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "Setup: Create Python Virtual Environment"
        )
        self.assertEqual(launch["args"], ["python", "--platform", "${input:setupPlatform}"])
        self.assertEqual(
            task["args"],
            ["-m", "tools.environment_setup", "python", "--platform", "${input:setupPlatform}"],
        )

    def test_task_setup_uses_internal_model_config(self) -> None:
        setup = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "Setup: Install Ollama and Pull Local LLM"
        )
        self.assertEqual(
            setup["args"],
            ["-m", "tools.environment_setup", "ollama", "--platform", "${input:setupPlatform}"],
        )
        self.assertTrue(any("Check File" in item["label"] for item in self.tasks["tasks"]))

    def test_ollama_server_task_is_foreground_process(self) -> None:
        task = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "Local LLM: Run Ollama Server (Foreground)"
        )
        self.assertEqual(task["type"], "process")
        self.assertNotIn("isBackground", task)
        self.assertEqual(
            task["args"],
            ["-m", "tools.environment_setup", "serve", "--platform", "${input:setupPlatform}"],
        )

    def test_platform_picker_supports_all_hosts(self) -> None:
        expected = ["config", "auto", "windows", "linux", "macos"]
        launch_input = next(item for item in self.launch["inputs"] if item["id"] == "setupPlatform")
        task_input = next(item for item in self.tasks["inputs"] if item["id"] == "setupPlatform")
        self.assertEqual(launch_input["options"], expected)
        self.assertEqual(task_input["options"], expected)
        self.assertEqual(launch_input["default"], "config")
        self.assertEqual(task_input["default"], "config")

    def test_python_commands_do_not_use_windows_venv_paths(self) -> None:
        for configuration in self.launch["configurations"]:
            self.assertNotIn("\\.venv\\Scripts\\", configuration.get("python", ""))
        for task in self.tasks["tasks"]:
            if task["label"] != "Package Electron":
                self.assertNotIn("\\.venv\\Scripts\\", task.get("command", ""))

    def test_python_tasks_run_as_managed_processes(self) -> None:
        for task in self.tasks["tasks"]:
            if task.get("command") == "${command:python.interpreterPath}":
                self.assertEqual(task["type"], "process")
                self.assertNotIn("isBackground", task)


if __name__ == "__main__":
    unittest.main()
