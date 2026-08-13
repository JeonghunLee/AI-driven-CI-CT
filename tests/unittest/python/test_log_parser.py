import unittest

from tools.log_parser import parse_text


class LogParserTests(unittest.TestCase):
    def test_numeric_error_metric_is_not_failure_log(self) -> None:
        parsed = parse_text("error=0.0001\nERROR connection lost")
        self.assertEqual(parsed.metrics["error"], 0.0001)
        self.assertEqual(parsed.errors, ["ERROR connection lost"])
        self.assertEqual(parsed.important, ["ERROR connection lost"])


if __name__ == "__main__":
    unittest.main()
