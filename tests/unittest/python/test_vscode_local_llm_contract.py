import json
import unittest
from pathlib import Path


class VSCodeLocalLLMContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launch = json.loads(Path(".vscode/launch.json").read_text(encoding="utf-8"))
        self.tasks = json.loads(Path(".vscode/tasks.json").read_text(encoding="utf-8"))
        self.config = json.loads(Path("tools/local_llm/model_config.json").read_text(encoding="utf-8"))

    def test_selected_preset_has_model_name(self) -> None:
        selected = self.config["selected"]
        self.assertIn(selected, self.config["models"])
        self.assertTrue(self.config["models"][selected]["name"])

    def test_launch_setup_uses_internal_model_config(self) -> None:
        setup = next(
            item for item in self.launch["configurations"]
            if item["name"] == "Setup 2: Install Ollama and Local LLM"
        )
        self.assertEqual(setup["args"], ["ollama"])
        self.assertTrue(any("Installed Models" in item["name"] for item in self.launch["configurations"]))

    def test_task_setup_uses_internal_model_config(self) -> None:
        setup = next(
            item for item in self.tasks["tasks"]
            if item["label"] == "Setup: Install Ollama and Pull Local LLM"
        )
        self.assertEqual(setup["args"], ["-m", "tools.environment_setup", "ollama"])
        self.assertTrue(any("Installed Models" in item["label"] for item in self.tasks["tasks"]))


if __name__ == "__main__":
    unittest.main()
