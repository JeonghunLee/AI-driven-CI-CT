from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


FORMATS = {"docx": ".docx", "pdf": ".pdf", "html": ".html"}
PANDOC_ROOT = Path("test_envs/reports/pandocs")


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
    executable = shutil.which("pandoc")
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
    subprocess.run(command, check=True)
    return destination


def latest_markdown(root: str | Path = "test_envs/reports") -> Path:
    candidates = list((Path(root) / "markdown").rglob("*_result.md"))
    if not candidates:
        raise FileNotFoundError("No Markdown report exists under test_envs/reports/markdown")
    return max(candidates, key=lambda path: path.name)


__all__ = ["FORMATS", "convert", "latest_markdown"]
