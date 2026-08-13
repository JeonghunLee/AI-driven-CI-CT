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

    def test_launch_setup_delegates_to_foreground_tasks(self) -> None:
        expected = {
            "Setup 1: Select Operating System": "Setup 1: Select Operating System",
            "Setup 2: Install Python Virtual Environment": "Setup 2: Install Python Virtual Environment",
            "Setup 3: Install Ollama and Local LLM": "Setup 3: Install Ollama and Local LLM",
            "Check 1: Refresh Environment Check File": "Check: Refresh Environment Check File",
        }
        configurations = {item["name"]: item for item in self.launch["configurations"]}
        for name, task in expected.items():
            configuration = configurations[name]
            self.assertEqual(configuration["preLaunchTask"], task)
            self.assertEqual(configuration["module"], "tools.configuration")
            self.assertEqual(configuration["args"], ["config"])
            self.assertNotEqual(configuration["module"], "tools.environment_setup")
        self.assertNotIn("inputs", self.launch)

    def test_python_setup_uses_platform_picker(self) -> None:
        task = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "Setup 2: Install Python Virtual Environment"
        )
        self.assertEqual(
            task["args"],
            ["-m", "tools.environment_setup", "python", "--platform", "config"],
        )

    def test_task_setup_uses_internal_model_config(self) -> None:
        setup = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "Setup 3: Install Ollama and Local LLM"
        )
        self.assertEqual(
            setup["args"],
            ["-m", "tools.environment_setup", "ollama", "--platform", "config"],
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
            ["-m", "tools.environment_setup", "serve", "--platform", "config"],
        )

    def test_platform_picker_supports_all_hosts(self) -> None:
        expected = ["auto", "windows", "linux", "macos"]
        task_input = next(item for item in self.tasks["inputs"] if item["id"] == "targetOS")
        self.assertEqual(task_input["options"], expected)
        self.assertEqual(task_input["default"], "auto")

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
