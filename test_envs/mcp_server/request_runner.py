from __future__ import annotations

import argparse
import json

from .runner import TestRequest, run_test


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute a GitHub Issue request through the Local MCP test runner layer"
    )
    parser.add_argument("--test-type", choices=["pytest", "unittest"], required=True)
    parser.add_argument("--test-id", default="")
    parser.add_argument("--fixture-mode", choices=["marker", "mock", "hil"], default="marker")
    parser.add_argument(
        "--unittest-scope",
        choices=["all", "ct_framework_python", "python", "c_cpp", "firmware", "common"],
        default="all",
    )
    parser.add_argument("--coverage", choices=["none", "terminal", "html"], default="none")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args()
    response = run_test(
        TestRequest(
            test_type=args.test_type,
            test_id=args.test_id,
            fixture_mode=args.fixture_mode,
            unittest_scope=args.unittest_scope,
            coverage=args.coverage,
            markdown=False,
            pandoc="none",
        ),
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(response, indent=2, ensure_ascii=False))
    if response.get("status") != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
