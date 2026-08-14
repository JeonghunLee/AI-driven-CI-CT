from __future__ import annotations

import argparse
import importlib
from collections.abc import Callable


def run(module_name: str) -> int:
    module = importlib.import_module(module_name)
    entrypoint: Callable[[], int | None] | None = getattr(module, "main", None)
    if not callable(entrypoint):
        raise RuntimeError(f"{module_name} must provide a callable main()")
    return entrypoint() or 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Generic entrypoint for future tools and controllers")
    parser.add_argument("--module", required=True, help="Python module exposing main()")
    args = parser.parse_args()
    raise SystemExit(run(args.module))


if __name__ == "__main__":
    main()
