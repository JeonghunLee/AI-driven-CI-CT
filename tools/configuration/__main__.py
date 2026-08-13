from __future__ import annotations

import argparse
import json

from . import SUPPORTED_OS, load_config, set_configured_os, write_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage project environment configuration")
    parser.add_argument("command", choices=["config", "check", "set-os"], nargs="?", default="check")
    parser.add_argument("--os", choices=SUPPORTED_OS, help="Operating system stored in config/config.json")
    args = parser.parse_args()
    if args.command == "config":
        value = load_config()
    elif args.command == "set-os":
        if args.os is None:
            parser.error("set-os requires --os")
        path = set_configured_os(args.os)
        value = {"config_file": str(path), "os": args.os}
    else:
        path = write_check()
        value = json.loads(path.read_text(encoding="utf-8"))
        value["check_file"] = str(path)
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
