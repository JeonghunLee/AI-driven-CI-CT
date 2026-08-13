import os
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import local_llm
from tools.local_llm import (
    DEFAULT_OLLAMA_MODEL,
    InstalledModel,
    LocalLLMAnalyzer,
    _resolve_model_from_config,
    selected_model,
    selected_url,
)


class LocalLLMTests(unittest.TestCase):
    def setUp(self) -> None:
        local_llm._load_config.cache_clear()

    def tearDown(self) -> None:
        local_llm._load_config.cache_clear()

    def test_explicit_model_has_highest_priority(self) -> None:
        with patch.dict(os.environ, {"OLLAMA_MODEL": "environment:model"}):
            self.assertEqual(selected_model("explicit:model"), "explicit:model")

    def test_environment_model_is_configurable(self) -> None:
        with patch.dict(os.environ, {"OLLAMA_MODEL": "custom:latest"}):
            self.assertEqual(LocalLLMAnalyzer().model, "custom:latest")

    def test_default_model_uses_latest_tag(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(selected_model(), DEFAULT_OLLAMA_MODEL)
            self.assertTrue(DEFAULT_OLLAMA_MODEL.endswith(":latest"))

    def test_internal_json_model_is_used_when_environment_is_missing(self) -> None:
        config = '{"model": "custom:latest"}'
        config_path = Path("reports/test-artifacts/local-llm/model-config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(config, encoding="utf-8")
        with patch.dict(os.environ, {"LOCAL_LLM_CONFIG": str(config_path)}, clear=True):
            self.assertEqual(selected_model(), "custom:latest")

    def test_internal_json_url_is_used_when_environment_is_missing(self) -> None:
        config = '{"url": "http://192.168.0.10:11434"}'
        config_path = Path("reports/test-artifacts/local-llm/url-config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(config, encoding="utf-8")
        with patch.dict(os.environ, {"LOCAL_LLM_CONFIG": str(config_path)}, clear=True):
            self.assertEqual(selected_url(), "http://192.168.0.10:11434")

    def test_object_preset_supports_extensible_model_metadata(self) -> None:
        config = {
            "selected": "reasoning",
            "models": {"reasoning": {"name": "model-family:latest", "role": "analysis"}},
        }
        self.assertEqual(_resolve_model_from_config(config), "model-family:latest")

    def test_installed_model_accepts_ollama_inventory_fields(self) -> None:
        model = InstalledModel.from_dict(
            {"name": "example:latest", "size": 42, "modified_at": "today", "digest": "abc"}
        )
        self.assertEqual(model.name, "example:latest")
        self.assertEqual(model.size, 42)


if __name__ == "__main__":
    unittest.main()
