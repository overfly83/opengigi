#!/usr/bin/env python3
import asyncio
from app.utils.logger import get_logger
"""
MCP Tools Integration

This module integrates MCP (Model Context Protocol) tools into the LangChain tool system
using langchain-mcp-adapters.
"""


from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import Dict, List, Any

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
            # "ppt": {
            #     "command": "uvx",
            #     "args": [
            #         "--from", "office-powerpoint-mcp-server", "ppt_mcp_server"
            #     ],
            #     "env": {},
            #     "transport": "stdio",
            # },

            "playwright": {
                "url": "http://localhost:8931/mcp",
                "transport": "http"
            }
        }
    )
    return mcp_client



