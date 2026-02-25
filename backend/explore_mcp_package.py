#!/usr/bin/env python3
"""
Explore MCP package structure
"""

import os
import langchain_mcp_adapters

# Get the package directory
package_dir = os.path.dirname(langchain_mcp_adapters.__file__)
print(f"MCP package directory: {package_dir}")

# List files in the package directory
print("\nFiles in the package directory:")
for item in os.listdir(package_dir):
    item_path = os.path.join(package_dir, item)
    if os.path.isfile(item_path):
        print(f"  File: {item}")
    elif os.path.isdir(item_path):
        print(f"  Directory: {item}")

# Check for any Python files
print("\nPython files in the package:")
for root, dirs, files in os.walk(package_dir):
    for file in files:
        if file.endswith('.py'):
            relative_path = os.path.relpath(os.path.join(root, file), package_dir)
            print(f"  {relative_path}")

# Try to import from submodules
try:
    from langchain_mcp_adapters import tools
    print("\nFound tools module")
    print(f"Available in tools: {dir(tools)}")
except ImportError as e:
    print(f"\nTools module not found: {e}")

try:
    from langchain_mcp_adapters import client
    print("\nFound client module")
    print(f"Available in client: {dir(client)}")
except ImportError as e:
    print(f"\nClient module not found: {e}")
