from __future__ import annotations

import argparse
import json
import os
import sys

from . import SUPPORTED_OS, load_config, set_configured_os, write_check


def _ensure_system_python() -> None:
    if sys.prefix == sys.base_prefix:
        return
    executable = getattr(sys, "_base_executable", None)
    if not executable:
        raise RuntimeError("System Python executable could not be resolved from the virtual environment")
    os.execv(executable, [executable, "-m", "test_envs.tools.configuration", *sys.argv[1:]])


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage project environment configuration")
    parser.add_argument("command", choices=["config", "check", "set-os", "select-os"], nargs="?", default="check")
    parser.add_argument("--os", choices=SUPPORTED_OS, help="Operating system stored in test_envs/config/config.json")
    args = parser.parse_args()
    if args.command == "config":
        value = load_config()
    elif args.command == "set-os":
        if args.os is None:
            parser.error("set-os requires --os")
        path = set_configured_os(args.os)
        value = {"config_file": str(path), "os": args.os}
    elif args.command == "select-os":
        _ensure_system_python()
        options = list(SUPPORTED_OS)
        print("Operating system:")
        for index, option in enumerate(options, start=1):
            print(f"  {index}. {option}")
        choice = input("Select [1]: ").strip() or "1"
        try:
            selected = options[int(choice) - 1]
        except (ValueError, IndexError):
            parser.error(f"invalid OS selection: {choice}")
        path = set_configured_os(selected)
        value = {"config_file": str(path), "os": selected}
    else:
        path = write_check()
        value = json.loads(path.read_text(encoding="utf-8"))
        value["check_file"] = str(path)
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
