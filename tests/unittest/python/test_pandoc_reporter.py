import pytest

from tools.pandoc_reporter import convert


def test_pandoc_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        convert("missing.md", "odt")
