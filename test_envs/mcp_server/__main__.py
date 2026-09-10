import os

from test_envs.mcp_server.runner import ROOT


os.chdir(ROOT)

from test_envs.mcp_server.server import mcp  # noqa: E402


if __name__ == "__main__":
    mcp.run()
