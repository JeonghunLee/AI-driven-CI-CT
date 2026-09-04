---
name: TEST Environment Check
about: Check the environment before requesting or running Pytest CT and Unittest
title: "[TEST-CHECK] "
labels: ""
assignees: ""
---

# TEST Environment Check

<br/>

Use this checklist before submitting `test_request.yml`. Complete the common section and only the sections that apply to the selected Test Type.

<br/>

## Request Information

<br/>

- Test Type: `pytest / CT` / `Unit Test`
- Branch / Tag / Commit:
- Runner:
- OS:
- Python:
- Date:

<br/>

## Common Environment

<br/>

- [ ] The repository was checked out at the requested Branch, Tag, or Commit.
- [ ] The configured OS in `test_envs/configs/config.json` matches the runner host or is `auto`.
- [ ] Project Python exists at `.venv/Scripts/python.exe` or `.venv/bin/python`.
- [ ] Dependencies from `requirements.txt` are installed.
- [ ] `test_envs/configs/check.json` was refreshed.
- [ ] Commands run from the repository root.
- [ ] The required source, configuration, and test files are present.

<br/>

## Pytest CT Environment

<br/>

- [ ] The selected TEST ID exists: `CT-UART-001`, `CT-USB-001`, or `CT-NETWORK-001`.
- [ ] The Test Case marker contains `test_id`, `category`, `fixture_id`, and `fixture_mode`.
- [ ] The numbered Test Case, Fixture ID, and Fixture argument agree.
- [ ] The selected Fixture declares the required Interface and Equipment.
- [ ] The final Fixture mode resolves to `mock` or `hil`.
- [ ] Mock mode is available when `mock` is selected.
- [ ] Physical hardware and handlers are available when `hil` is selected.
- [ ] HIL execution does not silently fall back to Mock.

<br/>

### Pytest Target

<br/>

- TEST ID:
- Fixture ID:
- Fixture Mode:
- Interface: UART / USB / JTAG / Network
- Equipment: FPGA / Saleae / Digilent / None
- Device / Board:
- Firmware:

<br/>

## Unittest Environment

<br/>

- [ ] The requested test exists under `test_envs/tests/unittest`.
- [ ] Pytest can collect the requested `unittest.TestCase` or test function.
- [ ] Native VS Code unittest discovery is disabled to prevent duplicate nodes.
- [ ] TEST ID, Fixture ID, and Mock/HIL mode are not required.
- [ ] The result will be aggregated by Execution ID.
- [ ] Local LLM analysis is not expected for Unittest.

<br/>

### Unittest Target

<br/>

- Scope: All / Directory / File / Function
- Pytest path or node ID:
- Expected test-function count:

<br/>

## Coverage Environment

<br/>

- [ ] `pytest-cov` is installed when Coverage is requested.
- [ ] The requested Coverage output is selected: terminal or HTML.
- [ ] `.coverage` and `htmlcov/` are treated as generated artifacts.
- [ ] Coverage scope is Python code coverage and does not represent physical HIL signal coverage.

<br/>

## Local LLM Environment - Pytest Only

<br/>

- [ ] Ollama is installed when Local LLM analysis is required.
- [ ] The configured Ollama endpoint is reachable.
- [ ] `ollama.selected_model` is installed.
- [ ] Timeout and retry settings are appropriate for the runner.
- [ ] The Local LLM log directory is writable.
- [ ] Deterministic fallback is acceptable if Ollama analysis fails.

<br/>

For Unittest, mark this section as not applicable because Local LLM is not used.

<br/>

## Report Environment

<br/>

- [ ] Result JSON and execution log directories are writable.
- [ ] `test_envs.tools.test_result --pending --docs` can generate Markdown.
- [ ] `docs/tests/pytest/` or `docs/tests/unittest/` is selected for MkDocs publication.
- [ ] Pandoc is installed and available on `PATH` when HTML or DOCX output is requested.
- [ ] `test_envs/reports/pandoc/` is writable when Pandoc output is requested.

<br/>

## GitHub Actions and Runner

<br/>

- [ ] The requested runner label is available.
- [ ] The runner has permission to read the repository and upload artifacts.
- [ ] GitHub-hosted Linux or Windows is selected for Mock CT or Unittest when physical hardware is not required.
- [ ] A GitHub-hosted run does not depend on local devices, vendor drivers, or an internal-only network.
- [ ] A self-hosted HIL runner has the matching `linux` or `windows` OS label.
- [ ] A self-hosted HIL runner has the required hardware, drivers, and device permissions.
- [ ] Physical HIL uses the matching `Self-hosted HIL Linux` or `Self-hosted HIL Windows` selection; GitHub-hosted execution is not treated as an HIL fallback.
- [ ] Required environment variables and secrets are configured without including secret values in this issue.
- [ ] Generated reports and logs are included in the workflow artifacts.

<br/>

## Check Result

<br/>

- [ ] READY - All applicable checks passed.
- [ ] BLOCKED - One or more required checks failed.

<br/>

### Blocking Items or Notes

<br/>

Describe missing software, unavailable hardware, configuration differences, or other blockers here.

<br/>
