from __future__ import annotations

from pathlib import Path
from shutil import copyfile
from threading import Event, Thread
from time import monotonic
from typing import Callable

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
        report_type = "unittest" if result.category.lower() == "unit" else "pytest"
        if report_type == "unittest":
            markdown = result_store.root / "markdown" / "unittest" / f"{result.execution_id}_result.md"
            document = Path(docs_root) / "tests" / "unittest" / f"{result.execution_id}.md"
        else:
            markdown = result_store.root / "markdown" / result.test_id / f"{result.execution_id}_result.md"
            document = Path(docs_root) / "tests" / "pytest" / f"{result.test_id}__{result.execution_id}.md"
        if not markdown.is_file() or (publish_docs and not document.is_file()):
            pending.append(result_path)
    return sorted(pending, key=lambda path: path.name)


def generate_pending_markdown(
    publish_docs: bool = False,
    review_source: bool = False,
    model: str | None = None,
    show_progress: bool = False,
) -> dict[str, object]:
    store = ResultStore()
    all_results = store.result_paths()
    pending = pending_result_paths(publish_docs=publish_docs, store=store)
    reports: list[dict[str, object]] = []
    total = len(pending)
    for index, result_path in enumerate(pending, start=1):
        result = store.load(result_path)
        action = lambda path=result_path: run(
            publish_docs=publish_docs,
            review_source=review_source,
            model=model,
            result_path=path,
        )
        if show_progress:
            reports.append(
                _run_with_progress(action, index, total, result.test_id, result.execution_id)
            )
        else:
            reports.append(action())
    return {
        "mode": "pending",
        "processed_count": len(reports),
        "skipped_count": len(all_results) - len(reports),
        "reports": reports,
    }


def _run_with_progress(
    action: Callable[[], dict[str, object]],
    index: int,
    total: int,
    test_id: str,
    execution_id: str,
) -> dict[str, object]:
    stop = Event()
    started = monotonic()
    label = f"[{index}/{total}]"

    def display() -> None:
        while not stop.wait(1.0):
            elapsed = int(monotonic() - started)
            print(f"{label} RUNNING {elapsed:03d}s {test_id} / {execution_id}", flush=True)

    print(f"{label} RUNNING 000s {test_id} / {execution_id}", flush=True)
    thread = Thread(target=display, name="markdown-progress", daemon=True)
    thread.start()
    status = "COMPLETE"
    try:
        return action()
    except Exception:
        status = "ERROR"
        raise
    finally:
        stop.set()
        thread.join(timeout=2.0)
        elapsed = int(monotonic() - started)
        print(f"{label} {status} {elapsed:03d}s {test_id} / {execution_id}", flush=True)


__all__ = [
    "generate_latest_markdown",
    "generate_pending_markdown",
    "pending_result_paths",
    "publish_latest",
]
