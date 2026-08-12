from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import ResultRecord, ResultStore, from_junit


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize a JSON test result")
    parser.add_argument("input", type=Path)
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--test-id", default="UNIT-TEST")
    args = parser.parse_args()
    if args.input.suffix.lower() == ".xml":
        record = from_junit(args.input, args.test_id)
    else:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        record = ResultRecord.from_dict(raw)
    destination = ResultStore(args.reports).save(record)
    if args.input.suffix.lower() == ".xml":
        (destination.parent / "junit.xml").write_bytes(args.input.read_bytes())
    print(destination)


if __name__ == "__main__":
    main()
