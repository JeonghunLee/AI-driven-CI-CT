from __future__ import annotations

import argparse
import json

from . import runtime_status, selected_model, selected_url


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Local LLM configuration and Ollama inventory")
    parser.add_argument("command", choices=["config", "status"], nargs="?", default="status")
    args = parser.parse_args()
    if args.command == "config":
        value = {"endpoint": selected_url(), "configured_model": selected_model()}
    else:
        value = runtime_status()
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
