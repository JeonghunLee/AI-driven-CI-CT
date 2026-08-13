from __future__ import annotations

import argparse
from contextlib import contextmanager
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
PLATFORMS = ("auto", "windows", "linux", "macos")


def _run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=check, text=True)


def setup_python(platform: str = "auto") -> None:
    platform = selected_platform(platform)
    print(f"Setup platform: {platform}", flush=True)
    if not VENV_PYTHON.exists():
        _run([sys.executable, "-m", "venv", str(VENV)])
    _run([str(VENV_PYTHON), "-m", "ensurepip", "--upgrade"])
    _run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"])
    _run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    print(f"Python environment ready: {VENV_PYTHON}")


def _host_platform() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    raise RuntimeError(f"unsupported host platform: {sys.platform}")


def selected_platform(platform: str = "auto") -> str:
    host = _host_platform()
    selected = host if platform == "auto" else platform
    if selected not in PLATFORMS[1:]:
        raise ValueError(f"unsupported setup platform: {platform}")
    if selected != host:
        raise RuntimeError(f"selected platform '{selected}' does not match host platform '{host}'")
    return selected


def _ollama_executable(platform: str) -> str | None:
    found = shutil.which("ollama")
    if found:
        return found
    if platform == "windows":
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            candidate = Path(local_app_data) / "Programs" / "Ollama" / "ollama.exe"
            if candidate.exists():
                return str(candidate)
    return None


def _install_ollama(platform: str) -> str:
    if platform == "windows":
        winget = shutil.which("winget")
        if not winget:
            raise RuntimeError("winget is required for automatic Ollama installation on Windows")
        _run([winget, "install", "--id", "Ollama.Ollama", "--exact", "--accept-source-agreements", "--accept-package-agreements"])
    elif platform == "macos":
        brew = shutil.which("brew")
        if not brew:
            raise RuntimeError("Homebrew is required for automatic Ollama installation on macOS")
        _run([brew, "install", "ollama"])
    elif platform == "linux":
        with tempfile.TemporaryDirectory(prefix="cict-ollama-") as temp_dir:
            installer = Path(temp_dir) / "install.sh"
            urlretrieve("https://ollama.com/install.sh", installer)
            _run(["sh", str(installer)])
    else:
        raise RuntimeError(f"automatic Ollama installation is unsupported on {platform}")
    executable = _ollama_executable(platform)
    if not executable:
        raise RuntimeError("Ollama was installed but its executable could not be located; restart VS Code and retry")
    return executable


def _ollama_ready(url: str) -> bool:
    try:
        with urlopen(f"{url.rstrip('/')}/api/tags", timeout=2) as response:
            return response.status == 200
    except (URLError, TimeoutError):
        return False


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


@contextmanager
def _ollama_server(executable: str, url: str):
    if _ollama_ready(url):
        yield
        return
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    process = subprocess.Popen(
        [executable, "serve"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    try:
        for _ in range(30):
            if _ollama_ready(url):
                yield
                return
            if process.poll() is not None:
                raise RuntimeError("Ollama server stopped before it became ready")
            time.sleep(1)
        raise RuntimeError("Ollama server did not become ready within 30 seconds")
    finally:
        _stop_process(process)


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


def setup_ollama(model: str | None = None, platform: str = "auto") -> None:
    model = selected_model(model)
    url = selected_url()
    platform = selected_platform(platform)
    print(f"Setup platform: {platform}", flush=True)
    if _is_local_endpoint(url):
        executable = _ollama_executable(platform) or _install_ollama(platform)
        with _ollama_server(executable, url):
            _setup_model(url, model)
        return
    if not _ollama_ready(url):
        raise RuntimeError(f"Remote Ollama is not reachable: {url}")
    _setup_model(url, model)


def _setup_model(url: str, model: str) -> None:
    print("Current Ollama inventory:")
    print(json.dumps(runtime_status(url), indent=2, ensure_ascii=False))
    _pull_model(url, model)
    print("Updated Ollama inventory:")
    print(json.dumps(runtime_status(url), indent=2, ensure_ascii=False))


def serve_ollama(platform: str = "auto") -> None:
    url = selected_url()
    platform = selected_platform(platform)
    if not _is_local_endpoint(url):
        raise RuntimeError(f"Cannot start a local Ollama server for remote endpoint: {url}")
    executable = _ollama_executable(platform) or _install_ollama(platform)
    print(f"+ {executable} serve", flush=True)
    print("Ollama is running in the foreground. Stop this task to stop the server.", flush=True)
    _run([executable, "serve"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up local CI/CT development dependencies")
    subparsers = parser.add_subparsers(dest="command", required=True)
    python_setup = subparsers.add_parser("python", help="Create .venv and install Python dependencies")
    python_setup.add_argument("--platform", choices=PLATFORMS, default="auto", help="Target platform; auto detects the host")
    ollama = subparsers.add_parser("ollama", help="Install Ollama, start it, and pull the selected Local LLM")
    ollama.add_argument(
        "--model",
        help=f"Ollama model; defaults to OLLAMA_MODEL or {DEFAULT_OLLAMA_MODEL}",
    )
    ollama.add_argument("--platform", choices=PLATFORMS, default="auto", help="Target platform; auto detects the host")
    serve = subparsers.add_parser("serve", help="Run the local Ollama server in the foreground")
    serve.add_argument("--platform", choices=PLATFORMS, default="auto", help="Target platform; auto detects the host")
    args = parser.parse_args()
    if args.command == "python":
        setup_python(args.platform)
    elif args.command == "ollama":
        setup_ollama(args.model, args.platform)
    else:
        serve_ollama(args.platform)


if __name__ == "__main__":
    main()
