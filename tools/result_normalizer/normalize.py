from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


def normalize_result(raw: dict[str, Any], commit: str, runner: str) -> dict[str, Any]:
    result = deepcopy(raw)
    result.setdefault("test_id", "UNKNOWN-TEST")
    result.setdefault("execution_id", datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    result.setdefault("status", "FAIL")
    result.setdefault("category", "unknown")
    result.setdefault("duration", 0.0)
    result.setdefault("interface", "None")
    result.setdefault("equipment", "None")
    result.setdefault("metrics", {})
    result.setdefault("statistics", {})
    result["commit"] = commit
    result["runner"] = runner

    test_id = result["test_id"]
    execution_id = result["execution_id"]
    result.setdefault(
        "logs",
        {
            "main": f"logs/{test_id}/{execution_id}/test.log",
            "stdout": f"logs/{test_id}/{execution_id}/stdout.log",
            "stderr": f"logs/{test_id}/{execution_id}/stderr.log",
            "equipment": f"logs/{test_id}/{execution_id}/equipment.log",
            "interface": f"logs/{test_id}/{execution_id}/interface.log",
        },
    )
    return result
