# AI-driven-CI-CT

AI-driven CI/CT with GitHub Actions, Self-hosted Runners, Ollama-first analysis, and Codex escalation.

## Key Principles

- GitHub is the single source of truth for repository, issue, PR, Actions, and artifacts.
- Unit test and pytest/CT are separated (`tests/unittest`, `tests/pytest`).
- pytest/CT separates test cases, test interfaces, and test equipment.
- Ollama is the default analysis layer; Codex is used only for escalation.
- Result, raw logs, and measurements are normalized and preserved.

## Structure

- `.github/ISSUE_TEMPLATE/test.yml`: Test request issue form
- `.github/workflows/unit-test.yml`: self-hosted unit test workflow
- `.github/workflows/continuous-test.yml`: self-hosted pytest/CT workflow
- `tools/result_normalizer`: result.json normalizer
- `tools/ollama`: Ollama-first result analyzer
- `tools/codex_escalation`: Codex escalation selector
- `tools/github_reporter`: Issue comment markdown renderer
- `tools/mkdocs_reporter`: MkDocs report markdown renderer
