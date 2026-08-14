import json
import unittest
from pathlib import Path


class VSCodeLocalLLMContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launch = json.loads(Path(".vscode/launch.json").read_text(encoding="utf-8"))
        self.tasks = json.loads(Path(".vscode/tasks.json").read_text(encoding="utf-8"))
        self.settings = json.loads(Path(".vscode/settings.json").read_text(encoding="utf-8"))
        self.config = json.loads(Path("test_envs/configs/unittest/config.json").read_text(encoding="utf-8"))

    def test_selected_preset_has_model_name(self) -> None:
        self.assertIn(self.config["os"], ["auto", "windows", "linux", "macos"])
        self.assertTrue(self.config["ollama"]["selected_model"])

    def test_launch_setup_delegates_to_foreground_tasks(self) -> None:
        expected = {
            "SETUP 1: Select Operating System": "SETUP 1: Select Operating System",
            "SETUP 2: Install Python Virtual Environment": "SETUP 2: Install Python Virtual Environment",
            "SETUP 3: Install Ollama and Local LLM": "SETUP 3: Install Ollama and Local LLM",
            "CHECK 1: Refresh Environment Check File": "CHECK 1: Refresh Environment Check File",
        }
        configurations = {item["name"]: item for item in self.launch["configurations"]}
        for name, task in expected.items():
            configuration = configurations[name]
            self.assertEqual(configuration["preLaunchTask"], task)
            self.assertEqual(configuration["module"], "test_envs.tools.configuration")
            self.assertEqual(configuration["args"], ["config"])
            self.assertNotEqual(configuration["module"], "test_envs.tools.environment_setup")
        self.assertNotIn("inputs", self.launch)

    def test_python_setup_uses_platform_picker(self) -> None:
        task = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "SETUP 2: Install Python Virtual Environment"
        )
        self.assertEqual(
            task["args"],
            ["-m", "test_envs.tools.environment_setup", "python"],
        )

    def test_task_setup_uses_internal_model_config(self) -> None:
        setup = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "SETUP 3: Install Ollama and Local LLM"
        )
        self.assertEqual(
            setup["args"],
            ["-m", "test_envs.tools.environment_setup", "ollama"],
        )
        self.assertTrue(any("Check File" in item["label"] for item in self.tasks["tasks"]))

    def test_ollama_server_task_is_foreground_process(self) -> None:
        task = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "CHECK 3: Run Ollama Server (Foreground)"
        )
        self.assertEqual(task["type"], "process")
        self.assertNotIn("isBackground", task)
        self.assertEqual(
            task["args"],
            ["-m", "test_envs.tools.environment_setup", "serve"],
        )

    def test_vscode_json_contains_no_os_metadata(self) -> None:
        self.assertEqual([item["id"] for item in self.tasks["inputs"]], ["testCaseId"])
        for configuration in self.launch["configurations"]:
            expected_python = (
                "python"
                if configuration["name"].startswith(("SETUP 1", "SETUP 2"))
                else "${config:python.defaultInterpreterPath}"
            )
            self.assertEqual(configuration["python"], expected_python)
            self.assertNotIn("windows", configuration)
            self.assertNotIn("linux", configuration)
            self.assertNotIn("osx", configuration)
        for task in self.tasks["tasks"]:
            expected_command = (
                "python"
                if task["label"].startswith(("SETUP 1", "SETUP 2"))
                else "${config:python.defaultInterpreterPath}"
            )
            self.assertEqual(task["command"], expected_command)
            self.assertNotIn("windows", task)
            self.assertNotIn("linux", task)
            self.assertNotIn("osx", task)

    def test_python_tasks_run_as_managed_processes(self) -> None:
        for task in self.tasks["tasks"]:
            self.assertEqual(task["type"], "process")
            self.assertNotIn("isBackground", task)

    def test_setup_1_uses_system_python(self) -> None:
        launch = next(
            item for item in self.launch["configurations"]
            if item["name"] == "SETUP 1: Select Operating System"
        )
        task = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "SETUP 1: Select Operating System"
        )
        self.assertEqual(launch["python"], "python")
        self.assertEqual(task["command"], "python")
        self.assertNotIn(".venv", json.dumps(launch))
        self.assertNotIn(".venv", json.dumps(task))

    def test_vscode_testing_uses_project_venv_and_pytest(self) -> None:
        self.assertEqual(
            self.settings["python.defaultInterpreterPath"],
            "${workspaceFolder}/.venv/Scripts/python.exe",
        )
        self.assertTrue(self.settings["python.testing.pytestEnabled"])
        self.assertFalse(self.settings["python.testing.unittestEnabled"])
        self.assertEqual(
            self.settings["python.testing.pytestArgs"],
            ["-p", "no:cacheprovider", "test_envs/tests/pytest", "test_envs/tests/unittest"],
        )

    def test_test_case_tasks_support_all_and_test_id(self) -> None:
        tasks = [item for item in self.tasks["tasks"] if item["label"].startswith("TEST CASE:")]
        self.assertEqual(
            [item["label"] for item in tasks],
            [
                "TEST CASE: ALL",
                "TEST CASE: TEST ID",
            ],
        )
        self.assertTrue(tasks[0]["group"]["isDefault"])
        self.assertFalse(tasks[1]["group"]["isDefault"])
        self.assertIn("${input:testCaseId}", tasks[1]["args"])

    def test_test_case_id_picker_matches_catalog(self) -> None:
        picker = next(item for item in self.tasks["inputs"] if item["id"] == "testCaseId")
        catalog = json.loads(
            Path("test_envs/configs/pytest/test_cases/catalog.json").read_text(encoding="utf-8")
        )
        test_ids = [item["test_id"] for item in catalog["test_cases"]]

        self.assertEqual(picker["type"], "pickString")
        self.assertEqual(picker["options"], test_ids)
        self.assertIn(picker["default"], test_ids)

    def test_report_tasks_include_html_and_docx(self) -> None:
        labels = {item["label"] for item in self.tasks["tasks"]}
        self.assertIn("REPORT: Convert Latest Markdown to HTML", labels)
        self.assertIn("REPORT: Convert Latest Markdown to DOCX", labels)


if __name__ == "__main__":
    unittest.main()
