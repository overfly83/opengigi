
from app.utils.logger import get_logger
from langchain_mcp_adapters.client import MultiServerMCPClient
"""
MCP Tools Integration

This module integrates MCP (Model Context Protocol) tools into the LangChain tool system
using langchain-mcp-adapters.
"""

logger = get_logger(__name__)

def initialize_mcp_client():
    mcp_client = MultiServerMCPClient(
        {
            # Add MCP servers here
            # Example configuration:
            # "math": {
            #     "command": "python",
            #     "args": ["/path/to/math_server.py"],
            #     "transport": "stdio",
            # },
            "ppt": {
                "command": "uvx",
                "args": [
                    "--from", "office-powerpoint-mcp-server", "ppt_mcp_server"
                ],
                "env": {},
                "transport": "stdio",
            },
            "playwright": {
                "command": "npx",
                "args": [
                    "-y", "@playwright/mcp@latest"
                ],
                "transport": "stdio",
            }
        }
    )
    return mcp_client

if __name__ == "__main__":
    import asyncio
    
    async def main():
        mcp_client = initialize_mcp_client()
        mcp_tools = await mcp_client.get_tools()
        for tool in mcp_tools:
            print(tool)
    
    asyncio.run(main())



