from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = ROOT.parent
CONFIG_DIR = ROOT / "configs" / "unittest"
CONFIG_PATH = CONFIG_DIR / "config.json"
CHECK_PATH = CONFIG_DIR / "check.json"
VSCODE_SETTINGS_PATH = WORKSPACE_ROOT / ".vscode" / "settings.json"
SUPPORTED_OS = ("auto", "windows", "linux", "macos")


def config_path() -> Path:
    override = os.getenv("LOCAL_LLM_CONFIG")
    return Path(override) if override else CONFIG_PATH


def load_config() -> dict[str, Any]:
    path = config_path()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Invalid project configuration: {path}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"Invalid project configuration root: {path}")
    return value


def configured_os() -> str:
    value = load_config().get("os", "auto")
    if not isinstance(value, str) or value not in SUPPORTED_OS:
        raise RuntimeError(f"Invalid configured OS: {value!r}")
    return value


def set_configured_os(value: str) -> Path:
    if value not in SUPPORTED_OS:
        raise ValueError(f"Invalid configured OS: {value!r}")
    config = load_config()
    config["os"] = value
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sync_vscode_interpreter(value)
    return CONFIG_PATH


def vscode_interpreter_path(value: str) -> str:
    resolved = detected_os() if value == "auto" else value
    if resolved == "windows":
        return "${workspaceFolder}/.venv/Scripts/python.exe"
    if resolved in {"linux", "macos"}:
        return "${workspaceFolder}/.venv/bin/python"
    raise RuntimeError(f"Unsupported VS Code interpreter OS: {resolved}")


def sync_vscode_interpreter(value: str | None = None) -> Path:
    selected = value or configured_os()
    try:
        settings = json.loads(VSCODE_SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Invalid VS Code settings: {VSCODE_SETTINGS_PATH}: {error}") from error
    if not isinstance(settings, dict):
        raise RuntimeError(f"Invalid VS Code settings root: {VSCODE_SETTINGS_PATH}")
    settings["python.defaultInterpreterPath"] = vscode_interpreter_path(selected)
    VSCODE_SETTINGS_PATH.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return VSCODE_SETTINGS_PATH


def detected_os() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    return sys.platform


def _ollama_executable() -> str | None:
    executable = shutil.which("ollama")
    if executable:
        return executable
    if os.name == "nt" and (local_app_data := os.getenv("LOCALAPPDATA")):
        candidate = Path(local_app_data) / "Programs" / "Ollama" / "ollama.exe"
        if candidate.exists():
            return str(candidate)
    return None


def _command_version(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
        return (result.stdout or result.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _ollama_inventory(url: str) -> tuple[bool, list[dict[str, Any]], str | None]:
    try:
        with urlopen(f"{url.rstrip('/')}/api/tags", timeout=3) as response:
            payload = json.load(response)
        models = payload.get("models", [])
        if not isinstance(models, list):
            raise ValueError("Ollama response does not contain a model list")
        return True, [model for model in models if isinstance(model, dict)], None
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        return False, [], str(error)


def build_check() -> dict[str, Any]:
    config = load_config()
    ollama = config.get("ollama", {})
    if not isinstance(ollama, dict):
        raise RuntimeError("Invalid project configuration: ollama must be an object")
    url = str(ollama.get("url", "http://127.0.0.1:11434")).rstrip("/")
    selected_model = str(ollama.get("selected_model", ""))
    executable = _ollama_executable()
    available, models, error = _ollama_inventory(url)
    model_names = [str(model.get("name") or model.get("model") or "") for model in models]
    result: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "os": {
            "configured": configured_os(),
            "detected": detected_os(),
            "name": platform.platform(),
        },
        "python": {
            "installed": bool(sys.executable),
            "executable": sys.executable,
            "version": platform.python_version(),
        },
        "ollama": {
            "installed": executable is not None,
            "executable": executable,
            "version": _command_version([executable, "--version"]) if executable else "",
            "available": available,
            "endpoint": url,
            "selected_model": selected_model,
            "selected_model_installed": selected_model in model_names,
            "supported_models": models,
        },
    }
    if error:
        result["ollama"]["error"] = error
    return result


def write_check() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CHECK_PATH.write_text(json.dumps(build_check(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return CHECK_PATH


__all__ = [
    "CHECK_PATH",
    "CONFIG_PATH",
    "SUPPORTED_OS",
    "build_check",
    "config_path",
    "configured_os",
    "detected_os",
    "load_config",
    "set_configured_os",
    "sync_vscode_interpreter",
    "vscode_interpreter_path",
    "write_check",
]
