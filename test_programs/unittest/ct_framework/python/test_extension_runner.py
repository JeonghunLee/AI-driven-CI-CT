import unittest

from test_envs.tools.extension_runner import run


class ExtensionRunnerTests(unittest.TestCase):
    def test_example_extension(self) -> None:
        self.assertEqual(run("test_envs.tools.extensions.example"), 0)


if __name__ == "__main__":
    unittest.main()
