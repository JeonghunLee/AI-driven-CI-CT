import json
import unittest
from pathlib import Path


class VSCodeLocalLLMContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launch = json.loads(Path(".vscode/launch.json").read_text(encoding="utf-8"))
        self.tasks = json.loads(Path(".vscode/tasks.json").read_text(encoding="utf-8"))
        self.settings = json.loads(Path(".vscode/settings.json").read_text(encoding="utf-8"))
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
            ["-m", "tools.environment_setup", "python"],
        )

    def test_task_setup_uses_internal_model_config(self) -> None:
        setup = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "Setup 3: Install Ollama and Local LLM"
        )
        self.assertEqual(
            setup["args"],
            ["-m", "tools.environment_setup", "ollama"],
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
            ["-m", "tools.environment_setup", "serve"],
        )

    def test_vscode_json_contains_no_os_metadata(self) -> None:
        self.assertNotIn("inputs", self.tasks)
        for configuration in self.launch["configurations"]:
            self.assertEqual(configuration["python"], "${command:python.interpreterPath}")
            self.assertNotIn("windows", configuration)
            self.assertNotIn("linux", configuration)
            self.assertNotIn("osx", configuration)
        for task in self.tasks["tasks"]:
            self.assertEqual(task["command"], "${command:python.interpreterPath}")
            self.assertNotIn("windows", task)
            self.assertNotIn("linux", task)
            self.assertNotIn("osx", task)

    def test_python_tasks_run_as_managed_processes(self) -> None:
        for task in self.tasks["tasks"]:
            self.assertEqual(task["type"], "process")
            self.assertNotIn("isBackground", task)

    def test_vscode_testing_uses_project_venv_and_pytest(self) -> None:
        self.assertEqual(
            self.settings["python.defaultInterpreterPath"],
            "${workspaceFolder}\\.venv\\Scripts\\python.exe",
        )
        self.assertTrue(self.settings["python.testing.pytestEnabled"])
        self.assertFalse(self.settings["python.testing.unittestEnabled"])
        self.assertEqual(
            self.settings["python.testing.pytestArgs"],
            ["-p", "no:cacheprovider", "tests/pytest", "tests/unittest"],
        )


if __name__ == "__main__":
    unittest.main()
