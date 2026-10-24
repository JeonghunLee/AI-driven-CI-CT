"""CLI adapter for the command-selected Ollama MCP test workflow."""

from __future__ import annotations

import argparse
import json

from .runner import run_ollama_test_plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an Ollama MCP test rule from test_config.json")
    parser.add_argument(
        "--command",
        default="",
        help="Command registered in test_envs/configs/test_config.json; empty uses default_command",
    )
    args = parser.parse_args()
    result = run_ollama_test_plan(
        args.command,
        progress=lambda message: print(f"[progress] {message}", flush=True),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
