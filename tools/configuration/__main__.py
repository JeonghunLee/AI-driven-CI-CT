from __future__ import annotations

import argparse
import json

from . import build_check, load_config, write_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect project environment configuration")
    parser.add_argument("command", choices=["config", "check"], nargs="?", default="check")
    args = parser.parse_args()
    if args.command == "config":
        value = load_config()
    else:
        path = write_check()
        value = json.loads(path.read_text(encoding="utf-8"))
        value["check_file"] = str(path)
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
