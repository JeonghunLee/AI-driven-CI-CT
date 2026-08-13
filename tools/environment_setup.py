from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen, urlretrieve

from tools.local_llm import DEFAULT_OLLAMA_MODEL, runtime_status, selected_model, selected_url

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=check, text=True)


def setup_python() -> None:
    if not VENV_PYTHON.exists():
        _run([sys.executable, "-m", "venv", str(VENV)])
    _run([str(VENV_PYTHON), "-m", "ensurepip", "--upgrade"])
    _run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"])
    _run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    print(f"Python environment ready: {VENV_PYTHON}")


def _ollama_executable() -> str | None:
    found = shutil.which("ollama")
    if found:
        return found
    if os.name == "nt":
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            candidate = Path(local_app_data) / "Programs" / "Ollama" / "ollama.exe"
            if candidate.exists():
                return str(candidate)
    return None


def _install_ollama() -> str:
    if sys.platform == "win32":
        winget = shutil.which("winget")
        if not winget:
            raise RuntimeError("winget is required for automatic Ollama installation on Windows")
        _run([winget, "install", "--id", "Ollama.Ollama", "--exact", "--accept-source-agreements", "--accept-package-agreements"])
    elif sys.platform == "darwin":
        brew = shutil.which("brew")
        if not brew:
            raise RuntimeError("Homebrew is required for automatic Ollama installation on macOS")
        _run([brew, "install", "ollama"])
    elif sys.platform.startswith("linux"):
        with tempfile.TemporaryDirectory(prefix="cict-ollama-") as temp_dir:
            installer = Path(temp_dir) / "install.sh"
            urlretrieve("https://ollama.com/install.sh", installer)
            _run(["sh", str(installer)])
    else:
        raise RuntimeError(f"automatic Ollama installation is unsupported on {sys.platform}")
    executable = _ollama_executable()
    if not executable:
        raise RuntimeError("Ollama was installed but its executable could not be located; restart VS Code and retry")
    return executable


def _ollama_ready(url: str) -> bool:
    try:
        with urlopen(f"{url.rstrip('/')}/api/tags", timeout=2) as response:
            return response.status == 200
    except (URLError, TimeoutError):
        return False


def _start_ollama(executable: str, url: str) -> None:
    if _ollama_ready(url):
        return
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    subprocess.Popen(
        [executable, "serve"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    for _ in range(30):
        if _ollama_ready(url):
            return
        time.sleep(1)
    raise RuntimeError("Ollama server did not become ready within 30 seconds")


def _is_local_endpoint(url: str) -> bool:
    return (urlparse(url).hostname or "").lower() in {"127.0.0.1", "localhost", "::1"}


def _pull_model(url: str, model: str) -> None:
    request = Request(
        f"{url.rstrip('/')}/api/pull",
        data=json.dumps({"model": model, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print(f"+ pull {model} from {url}", flush=True)
    with urlopen(request, timeout=3600) as response:
        payload = json.load(response)
    if payload.get("status") != "success":
        raise RuntimeError(f"Ollama pull failed: {payload}")


def setup_ollama(model: str | None = None) -> None:
    model = selected_model(model)
    url = selected_url()
    if _is_local_endpoint(url):
        executable = _ollama_executable() or _install_ollama()
        _start_ollama(executable, url)
    elif not _ollama_ready(url):
        raise RuntimeError(f"Remote Ollama is not reachable: {url}")
    print("Current Ollama inventory:")
    print(json.dumps(runtime_status(url), indent=2, ensure_ascii=False))
    _pull_model(url, model)
    print("Updated Ollama inventory:")
    print(json.dumps(runtime_status(url), indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up local CI/CT development dependencies")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("python", help="Create .venv and install Python dependencies")
    ollama = subparsers.add_parser("ollama", help="Install Ollama, start it, and pull the selected Local LLM")
    ollama.add_argument(
        "--model",
        help=f"Ollama model; defaults to OLLAMA_MODEL or {DEFAULT_OLLAMA_MODEL}",
    )
    args = parser.parse_args()
    if args.command == "python":
        setup_python()
    else:
        setup_ollama(args.model)


if __name__ == "__main__":
    main()
