#!/usr/bin/env python3
"""
Check MCP imports
"""

import langchain_mcp_adapters
print("Available imports in langchain_mcp_adapters:")
print(dir(langchain_mcp_adapters))

# Try to find MCP-related imports
try:
    from langchain_mcp_adapters import MCPClient
    print("Found MCPClient")
except ImportError as e:
    print(f"MCPClient not found: {e}")

try:
    from langchain_mcp_adapters import MCPTool
    print("Found MCPTool")
except ImportError as e:
    print(f"MCPTool not found: {e}")

try:
    from langchain_mcp_adapters import MCP
    print("Found MCP")
except ImportError as e:
    print(f"MCP not found: {e}")
