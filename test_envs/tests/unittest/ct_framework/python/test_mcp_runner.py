import os
import sys
import unittest
from unittest.mock import patch

from mcp import Client, StdioServerParameters

from test_envs.mcp_server.runner import TestRequest as MCPTestRequest
from test_envs.mcp_server.runner import (
    _pytest_command,
    all_test_lists,
    pytest_test_list,
    run_test,
    unittest_test_list,
    update_mkdocs,
)
from test_envs.mcp_server.server import mcp
from test_envs.tools.test_catalog import catalog_tests


class MCPRunnerTests(unittest.TestCase):
    def test_pytest_list_exposes_allowlisted_ids_and_hil_gate(self) -> None:
        with patch.dict(os.environ, {"PYTEST_HIL_ALLOW": "false"}):
            value = pytest_test_list()

        self.assertEqual(
            [item["test_id"] for item in value["test_ids"]],
            [item["test_id"] for item in catalog_tests()],
        )
        self.assertFalse(value["pytest_hil_allow"])

    def test_unittest_list_exposes_extension_scopes(self) -> None:
        scopes = {item["scope"] for item in unittest_test_list()["scopes"]}
        self.assertEqual(
            scopes,
            {"all", "ct_framework_python", "python", "c_cpp", "firmware", "common"},
        )
        self.assertIn("pytest", all_test_lists())

    def test_pytest_command_uses_allowlisted_arguments_without_a_shell(self) -> None:
        command = _pytest_command(
            MCPTestRequest(
                test_type="pytest",
                test_id="CT-USB-001",
                fixture_mode="mock",
                coverage="html",
            )
        )

        self.assertIn("CT-USB-001", command)
        self.assertIn("mock", command)
        self.assertIn("--cov-report=html", command)

    def test_hil_requires_explicit_pytest_opt_in(self) -> None:
        request = MCPTestRequest(
            test_type="pytest",
            test_id=catalog_tests()[0]["test_id"],
            fixture_mode="hil",
        )
        with patch.dict(os.environ, {"PYTEST_HIL_ALLOW": "false"}):
            with self.assertRaisesRegex(PermissionError, "PYTEST_HIL_ALLOW"):
                run_test(request)

    def test_mkdocs_update_requires_explicit_opt_in(self) -> None:
        with patch.dict(os.environ, {"MKDOC_UPDATE": "false"}):
            with self.assertRaisesRegex(PermissionError, "MKDOC_UPDATE"):
                update_mkdocs("unittest")

    def test_rejects_unknown_test_id_before_starting_process(self) -> None:
        request = MCPTestRequest(test_type="pytest", test_id="CT-UNKNOWN-999")
        with self.assertRaisesRegex(ValueError, "test_id"):
            run_test(request)


class MCPServerContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_client_discovers_and_calls_test_inventory(self) -> None:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            result = await client.call_tool("get_test_list_all", {})

        self.assertEqual(
            {tool.name for tool in tools.tools},
            {
                "get_test_envs",
                "get_test_list_pytest",
                "get_test_list_unittest",
                "get_test_list_all",
                "get_github_issue_requests",
                "run_test_pytest",
                "run_test_unittest",
                "run_test_all",
                "run_github_issue",
                "update_latest_result",
                "update_mkdocs",
            },
        )
        self.assertEqual(
            [item["test_id"] for item in result.structured_content["pytest"]["test_ids"]],
            [item["test_id"] for item in catalog_tests()],
        )

    @unittest.skipUnless(
        os.getenv("AI_CT_RUN_STDIO_TEST", "false").lower() == "true",
        "set AI_CT_RUN_STDIO_TEST=true to launch the external stdio process",
    )
    async def test_stdio_client_launches_external_server_process(self) -> None:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "test_envs.mcp_server"],
            cwd=os.getcwd(),
            env={"PYTEST_HIL_ALLOW": "false", "MKDOC_UPDATE": "false"},
        )
        async with Client(parameters) as client:
            tools = await client.list_tools()

        self.assertIn("run_test_pytest", {tool.name for tool in tools.tools})


if __name__ == "__main__":
    unittest.main()
