from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


def parse_issue_body(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    parts = re.split(r"^###\s+", body, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.splitlines()
        label = lines[0].strip()
        value = "\n".join(lines[1:]).strip()
        if value and value != "_No response_":
            fields[label] = value
    return fields


def event_configuration(event_path: str | Path) -> dict[str, str]:
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    if "issue" in event:
        fields = parse_issue_body(event["issue"].get("body", ""))
        return {
            "test_type": fields.get("Test Type", "pytest / CT"),
            "category": fields.get("Test Category", "Timing"),
            "runner": fields.get("Runner", "Default"),
        }
    inputs = event.get("inputs", {})
    return {"test_type": "pytest / CT", "category": "Timing", "runner": inputs.get("runner", "Default")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("event", nargs="?", default=os.getenv("GITHUB_EVENT_PATH"))
    parser.add_argument("--github-output", default=os.getenv("GITHUB_OUTPUT"))
    args = parser.parse_args()
    if not args.event:
        raise SystemExit("event path is required")
    config = event_configuration(args.event)
    output = "\n".join(f"{key}={value}" for key, value in config.items()) + "\n"
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as stream:
            stream.write(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
