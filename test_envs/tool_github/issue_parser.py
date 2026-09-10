from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


RUNNER_LABELS = {
    "GitHub-hosted Linux": ["ubuntu-latest"],
    "GitHub-hosted Windows": ["windows-latest"],
    "Self-hosted HIL Linux": ["self-hosted", "linux", "hw-test"],
    "Self-hosted HIL Windows": ["self-hosted", "windows", "hw-test"],
}

RUNNER_ALIASES = {
    "Default": "GitHub-hosted Linux",
    "Linux": "GitHub-hosted Linux",
    "Windows": "GitHub-hosted Windows",
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
    runner = values.get("Runner", values.get("runner", "GitHub-hosted Linux"))
    runner = RUNNER_ALIASES.get(runner, runner)
    if runner not in RUNNER_LABELS:
        choices = ", ".join(RUNNER_LABELS)
        raise ValueError(f"unsupported runner {runner!r}; select one of: {choices}")
    reports = values.get("Report Outputs", values.get("reports", ""))
    test_type = values.get("Test Type", values.get("test_type", "Pytest"))
    test_type = TEST_TYPE_ALIASES.get(test_type, test_type)
    if test_type not in {"Pytest", "Unittest"}:
        raise ValueError(f"unsupported test type: {test_type!r}")
    unittest_target = _first_line(
        values.get("Unittest Target", values.get("unittest_target", "")),
        "test_envs/tests/unittest",
    )
    if unittest_target.upper() == "N/A":
        unittest_target = "test_envs/tests/unittest"
    return {
        "test_type": test_type,
        "test_id": values.get("Test ID", values.get("test_id", "CT-UART-001")),
        "fixture_mode": values.get("Fixture Mode", values.get("fixture_mode", "marker")),
        "unittest_scope": values.get("Unittest Scope", values.get("unittest_scope", "All Unittest")),
        "unittest_target": unittest_target,
        "runner": runner,
        "runner_labels": json.dumps(RUNNER_LABELS[runner], separators=(",", ":")),
        "request_ref": values.get("Branch / Tag / Commit", values.get("request_ref", "main")),
        "coverage": values.get("Test Coverage", values.get("coverage", "No coverage")),
        "report_mkdocs": _checked(reports, "MkDocs Markdown"),
        "report_html": _checked(reports, "Pandoc HTML"),
        "report_docx": _checked(reports, "Pandoc DOCX"),
    }


def event_configuration(event_path: str | Path) -> dict[str, str]:
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    if "issue" in event:
        values = parse_issue_body(event["issue"].get("body", ""))
        title = str(event["issue"].get("title", ""))
        if title.startswith("[UNITTEST-REQUEST]"):
            values["Test Type"] = "Unittest"
        elif title.startswith("[PYTEST-REQUEST]"):
            values["Test Type"] = "Pytest"
        config = request_configuration(values)
        labels = {
            str(item.get("name", ""))
            for item in event["issue"].get("labels", [])
            if isinstance(item, dict)
        }
        is_environment_check = "test-check-runner" in labels or title.startswith("[TEST-CHECK]")
        config["request_kind"] = "environment-check" if is_environment_check else "test"
        return config
    inputs = {str(key): str(value) for key, value in event.get("inputs", {}).items()}
    report_values = []
    if inputs.get("report_mkdocs", "true").lower() == "true":
        report_values.append("- [x] MkDocs Markdown")
    if inputs.get("report_html", "false").lower() == "true":
        report_values.append("- [x] Pandoc HTML")
    if inputs.get("report_docx", "false").lower() == "true":
        report_values.append("- [x] Pandoc DOCX")
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
