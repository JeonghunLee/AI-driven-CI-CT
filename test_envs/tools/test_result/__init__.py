from __future__ import annotations

from pathlib import Path
from shutil import copyfile

from test_envs.tools.pipeline import run

LATEST_MARKDOWN = Path(__file__).resolve().parent / "markdown" / "latest.md"


def publish_latest(source: str | Path, destination: str | Path = LATEST_MARKDOWN) -> Path:
    source_path = Path(source)
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    copyfile(source_path, destination_path)
    return destination_path


def generate_latest_markdown(
    publish_docs: bool = False,
    review_source: bool = False,
    model: str | None = None,
) -> dict[str, object]:
    """Generate Markdown from the newest result without running tests."""
    output = run(publish_docs=publish_docs, review_source=review_source, model=model)
    output["latest_markdown"] = str(publish_latest(str(output["markdown"])))
    return output


__all__ = ["LATEST_MARKDOWN", "generate_latest_markdown", "publish_latest"]
