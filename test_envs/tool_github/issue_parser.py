from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from test_envs.tools.test_catalog import catalog_by_id, catalog_tests


RUNNER_LABELS = {
    ("GitHub-hosted Runner", "ubuntu"): ["ubuntu-latest"],
    ("GitHub-hosted Runner", "windows"): ["windows-latest"],
    ("Self-hosted Runner", "ubuntu"): ["self-hosted", "linux", "hw-test"],
    ("Self-hosted Runner", "windows"): ["self-hosted", "windows", "hw-test"],
    ("Local MCP", "ubuntu"): [],
    ("Local MCP", "windows"): [],
}

ENVIRONMENT_VALUES = {
    "GitHub-hosted Runner": "github_hosted_runner",
    "Self-hosted Runner": "self_hosted_runner",
    "Local MCP": "local",
}

ENVIRONMENT_ALIASES = {
    "github_hosted_runner": "GitHub-hosted Runner",
    "self_hosted_runner": "Self-hosted Runner",
    "local": "Local MCP",
}

OS_ALIASES = {
    "Linux": "ubuntu",
    "Ubuntu": "ubuntu",
    "ubuntu": "ubuntu",
    "Windows": "windows",
    "Window": "windows",
    "windows": "windows",
}

LEGACY_RUNNERS = {
    "Default": ("GitHub-hosted Runner", "ubuntu"),
    "Linux": ("GitHub-hosted Runner", "ubuntu"),
    "Windows": ("GitHub-hosted Runner", "windows"),
    "GitHub-hosted Linux": ("GitHub-hosted Runner", "ubuntu"),
    "GitHub-hosted Windows": ("GitHub-hosted Runner", "windows"),
    "Self-hosted HIL Linux": ("Self-hosted Runner", "ubuntu"),
    "Self-hosted HIL Windows": ("Self-hosted Runner", "windows"),
}

TEST_TYPE_ALIASES = {
    "pytest / CT": "Pytest",
    "Unit Test": "Unittest",
}


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


def _first_line(value: str, default: str) -> str:
    for line in value.splitlines():
        selected = line.strip()
        if selected and selected != "_No response_":
            return selected
    return default


def _checked(value: str, label: str) -> str:
    return str(bool(re.search(rf"^- \[[xX]\]\s+{re.escape(label)}\s*$", value, re.MULTILINE))).lower()


def request_configuration(values: dict[str, str]) -> dict[str, str]:
    legacy_runner = values.get("Runner", values.get("runner", ""))
    if legacy_runner:
        try:
            execution_host, test_os = LEGACY_RUNNERS[legacy_runner]
        except KeyError as error:
            raise ValueError(f"unsupported legacy runner: {legacy_runner!r}") from error
    else:
        execution_host = values.get(
            "Test Environment",
            values.get("test_environment", "GitHub-hosted Runner"),
        )
        execution_host = ENVIRONMENT_ALIASES.get(execution_host, execution_host)
        raw_os = values.get("Operating System", values.get("test_os", "Ubuntu"))
        test_os = OS_ALIASES.get(raw_os, raw_os.lower())
    if execution_host not in ENVIRONMENT_VALUES:
        raise ValueError(f"unsupported test environment: {execution_host!r}")
    runner_key = (execution_host, test_os)
    if runner_key not in RUNNER_LABELS:
        raise ValueError(f"unsupported test environment and OS combination: {runner_key!r}")
    reports = values.get("Report Outputs", values.get("reports", ""))
    test_type = values.get("Test Type", values.get("test_type", "Pytest"))
    test_type = TEST_TYPE_ALIASES.get(test_type, test_type)
    if test_type not in {"Pytest", "Unittest"}:
        raise ValueError(f"unsupported test type: {test_type!r}")
    test_id = ""
    if test_type == "Pytest":
        catalog = catalog_by_id()
        tests = catalog_tests()
        if not tests:
            raise ValueError("Pytest test catalog is empty")
        default_test_id = str(tests[0]["test_id"])
        test_id = values.get("Test ID", values.get("test_id", default_test_id))
        if test_id not in catalog:
            raise ValueError(f"unsupported TEST ID {test_id!r}; select one of: {', '.join(catalog)}")
    unittest_target = _first_line(
        values.get("Unittest Target", values.get("unittest_target", "")),
        "test_envs/tests/unittest",
    )
    if unittest_target.upper() == "N/A":
        unittest_target = "test_envs/tests/unittest"
    return {
        "test_type": test_type,
        "test_id": test_id,
        "fixture_mode": values.get("Fixture Mode", values.get("fixture_mode", "marker")),
        "unittest_scope": values.get("Unittest Scope", values.get("unittest_scope", "All Unittest")),
        "unittest_target": unittest_target,
        "execution_host": execution_host,
        "test_environment": ENVIRONMENT_VALUES[execution_host],
        "test_os": test_os,
        "runner_labels": json.dumps(RUNNER_LABELS[runner_key], separators=(",", ":")),
        "request_ref": values.get("Branch / Tag / Commit", values.get("request_ref", "main")),
        "coverage": values.get("Test Coverage", values.get("coverage", "No coverage")),
        "report_log": _checked(reports, "Log"),
        "report_markdown": _checked(reports, "Markdown"),
        "report_mkdocs": _checked(reports, "MkDocs Markdown"),
        "report_docx": _checked(reports, "Pandoc DOCX"),
        "report_html": _checked(reports, "Pandoc HTML"),
    }


def issue_configuration(issue: dict[str, object]) -> dict[str, str]:
    values = parse_issue_body(str(issue.get("body", "")))
    title = str(issue.get("title", ""))
    labels = {
        str(item.get("name", ""))
        for item in issue.get("labels", [])
        if isinstance(item, dict)
    }
    is_environment_check = "test-check-runner" in labels or title.startswith("[TEST-CHECK]")
    if title.startswith("[UNITTEST-REQUEST]"):
        values["Test Type"] = "Unittest"
    elif title.startswith("[PYTEST-REQUEST]"):
        values["Test Type"] = "Pytest"
    elif is_environment_check:
        values["Test Type"] = "Unittest"
    config = request_configuration(values)
    config["request_kind"] = "environment-check" if is_environment_check else "test"
    return config


def event_configuration(event_path: str | Path) -> dict[str, str]:
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    if "issue" in event:
        return issue_configuration(event["issue"])
    inputs = {str(key): str(value) for key, value in event.get("inputs", {}).items()}
    report_values = []
    if inputs.get("report_log", "true").lower() == "true":
        report_values.append("- [x] Log")
    if inputs.get("report_markdown", "true").lower() == "true":
        report_values.append("- [x] Markdown")
    if inputs.get("report_mkdocs", "true").lower() == "true":
        report_values.append("- [x] MkDocs Markdown")
    if inputs.get("report_docx", "false").lower() == "true":
        report_values.append("- [x] Pandoc DOCX")
    if inputs.get("report_html", "false").lower() == "true":
        report_values.append("- [x] Pandoc HTML")
    inputs["reports"] = "\n".join(report_values)
    config = request_configuration(inputs)
    config["request_kind"] = "test"
    return config


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
