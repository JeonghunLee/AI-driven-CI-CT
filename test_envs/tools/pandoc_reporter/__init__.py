from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


FORMATS = {"docx": ".docx", "pdf": ".pdf", "html": ".html"}
PANDOC_ROOT = Path("test_reports/pandocs")
REFERENCE_CONFIG = Path("docx/setup_reference.json")


def _reference_manifest() -> dict[str, object]:
    """Read the editable Pandoc reference configuration."""
    try:
        value = json.loads(REFERENCE_CONFIG.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Pandoc reference manifest does not exist: {REFERENCE_CONFIG}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Pandoc reference manifest is invalid JSON: {REFERENCE_CONFIG}") from error

    if not isinstance(value, dict):
        raise ValueError(f"Pandoc reference manifest must be a JSON object: {REFERENCE_CONFIG}")
    return value


def _reference_document() -> Path:
    """Return the Word style reference selected in the editable manifest."""
    reference = _reference_manifest().get("reference_docx")
    if not isinstance(reference, str) or not reference:
        raise ValueError("Pandoc reference manifest requires a non-empty reference_docx")
    reference_path = Path(reference)
    if reference_path.parent != Path("docx/reference"):
        raise ValueError("Pandoc reference_docx must be stored under docx/reference")
    return reference_path


REFERENCE_DOC = _reference_document()


def additional_docx_args() -> list[str]:
    """Return optional DOCX-only arguments configured for every report."""
    manifest = _reference_manifest()
    pandoc = manifest.get("pandoc")
    if not isinstance(pandoc, dict):
        raise ValueError("Pandoc reference manifest requires a pandoc object")
    args = pandoc.get("add_doc_args", [])
    if not isinstance(args, list) or not all(isinstance(argument, str) for argument in args):
        raise ValueError("Pandoc add_doc_args must be a string list")
    return args


def pandoc_executable() -> str | None:
    """Find Pandoc, including its standard Windows per-user install location."""
    executable = shutil.which("pandoc")
    if executable:
        return executable

    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        per_user_install = Path(local_app_data) / "Pandoc" / "pandoc.exe"
        if per_user_install.is_file():
            return str(per_user_install)

    try:
        import pypandoc

        bundled_install = Path(pypandoc.get_pandoc_path())
        if bundled_install.is_file():
            return str(bundled_install)
    except (ImportError, OSError, RuntimeError):
        pass
    return None


def _default_output_dir(source_path: Path) -> Path:
    report_group = source_path.parent.name
    if report_group == "unittest":
        return PANDOC_ROOT / "unittest"
    return PANDOC_ROOT / "pytest" / "test_cases" / report_group


def convert(source: str | Path, output_format: str, output_dir: str | Path | None = None) -> Path:
    source_path = Path(source)
    if output_format not in FORMATS:
        raise ValueError(f"unsupported Pandoc format: {output_format}")
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    executable = pandoc_executable()
    if not executable:
        raise RuntimeError("Pandoc is not installed or is not available on PATH")
    destination_dir = (
        Path(output_dir)
        if output_dir
        else _default_output_dir(source_path)
    )
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{source_path.stem}{FORMATS[output_format]}"
    command = [executable, str(source_path), "-o", str(destination), "--standalone"]
    if output_format == "docx":
        if not REFERENCE_DOC.is_file():
            raise FileNotFoundError(f"Pandoc reference DOCX does not exist: {REFERENCE_DOC}")
        command.extend(additional_docx_args())
        command.extend(["--reference-doc", str(REFERENCE_DOC)])
    subprocess.run(command, check=True)
    return destination


def latest_markdown(root: str | Path = "test_reports") -> Path:
    candidates = list((Path(root) / "markdown").rglob("*_result.md"))
    if not candidates:
        raise FileNotFoundError("No Markdown report exists under test_reports/markdown")
    return max(candidates, key=lambda path: path.name)


__all__ = [
    "FORMATS",
    "PANDOC_ROOT",
    "REFERENCE_CONFIG",
    "REFERENCE_DOC",
    "pandoc_executable",
    "additional_docx_args",
    "convert",
    "latest_markdown",
]
