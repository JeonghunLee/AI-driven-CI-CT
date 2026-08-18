from __future__ import annotations

from pathlib import Path
from shutil import copyfile

from test_envs.tools.pipeline import run
from test_envs.tools.result_normalizer import ResultStore

def publish_latest(source: str | Path, destination: str | Path) -> Path:
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
    output["latest_markdown"] = str(output["markdown"])
    return output


def pending_result_paths(
    publish_docs: bool = False,
    store: ResultStore | None = None,
    docs_root: str | Path = "docs",
) -> list[Path]:
    result_store = store or ResultStore()
    pending: list[Path] = []
    for result_path in result_store.result_paths():
        result = result_store.load(result_path)
        markdown = (
            result_store.root
            / "markdown"
            / result.test_id
            / f"{result.execution_id}_result.md"
        )
        report_type = "unittest" if result.category.lower() == "unit" else "pytest"
        document = (
            Path(docs_root)
            / "tests"
            / report_type
            / f"{result.test_id}__{result.execution_id}.md"
        )
        if not markdown.is_file() or (publish_docs and not document.is_file()):
            pending.append(result_path)
    return sorted(pending, key=lambda path: path.name)


def generate_pending_markdown(
    publish_docs: bool = False,
    review_source: bool = False,
    model: str | None = None,
) -> dict[str, object]:
    store = ResultStore()
    all_results = store.result_paths()
    pending = pending_result_paths(publish_docs=publish_docs, store=store)
    reports = [
        run(
            publish_docs=publish_docs,
            review_source=review_source,
            model=model,
            result_path=result_path,
        )
        for result_path in pending
    ]
    return {
        "mode": "pending",
        "processed_count": len(reports),
        "skipped_count": len(all_results) - len(reports),
        "reports": reports,
    }


__all__ = [
    "generate_latest_markdown",
    "generate_pending_markdown",
    "pending_result_paths",
    "publish_latest",
]
