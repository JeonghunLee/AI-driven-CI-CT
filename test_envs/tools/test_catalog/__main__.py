from __future__ import annotations

import json

from . import CATALOG_PATH, generate_catalog


def main() -> None:
    catalog = generate_catalog(sync_consumers=True)
    print(
        json.dumps(
            {
                "catalog": str(CATALOG_PATH),
                "test_count": len(catalog["tests"]),
                "test_ids": [test["test_id"] for test in catalog["tests"]],
                "synchronized": [
                    ".vscode/tasks.json",
                    ".github/ISSUE_TEMPLATE/pytest_request.yml",
                    ".github/workflows/continuous-test.yml",
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
