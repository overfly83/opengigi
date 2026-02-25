#!/usr/bin/env python3
import asyncio
"""
LangChain Tool Registry

This module manages the registration and discovery of LangChain tools.
"""

import importlib
import os
from typing import Dict, List, Callable, Any

# 导入自定义日志
from app.utils.logger import get_logger

class ToolRegistry:
    """Registry for managing LangChain tools"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.logger = get_logger(__name__)

    def register_tool(self, tool_func) -> None:
        """Register a new LangChain tool"""
        if hasattr(tool_func, 'name'):
            tool_name = tool_func.name
        elif hasattr(tool_func, '__name__'):
            tool_name = tool_func.__name__
        else:
            self.logger.warning(f"Tool object has no name attribute: {tool_func}")
        
        if tool_name in self.tools:
            raise ValueError(f"Tool {tool_name} already registered")
        self.tools[tool_name] = tool_func
    
    def get_tool(self, name: str) -> Callable:
        """Get a registered tool by name"""
        if name not in self.tools:
            self.logger.error(f"Tool {name} not found")
        return self.tools[name]
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all registered tools"""
        return [
            {"name": name, "description": getattr(tool, 'description', '')}
            for name, tool in self.tools.items()
        ]
    
    def list_mcp_tools(self) -> List[Dict[str, str]]:
        """List all registered MCP tools"""
        return [
            {"name": name, "description": getattr(tool, 'description', '')}
            for name, tool in self.tools.items()
            if getattr(tool, 'is_mcp', False)
        ]
    
    def list_regular_tools(self) -> List[Dict[str, str]]:
        """List all registered regular tools"""
        return [
            {"name": name, "description": getattr(tool, 'description', '')}
            for name, tool in self.tools.items()
            if not getattr(tool, 'is_mcp', False)
        ]
    
    def list_tools_with_type(self) -> List[Dict[str, str]]:
        """List all registered tools with their type (MCP or regular)"""
        return [
            {
                "name": name, 
                "description": getattr(tool, 'description', ''),
                "type": "mcp" if getattr(tool, 'is_mcp', False) else "regular"
            }
            for name, tool in self.tools.items()
        ]
    
    async def load_tools(self) -> List[Callable]:
        """Load all LangChain tools from the tools directory
        
        Returns:
            List of tool instances
        """
        tools_dir = os.path.dirname(__file__)
        
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base.py', 'registry.py']:
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'app.tools.{module_name}')
                    
                    # Find all tool-decorated functions in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        try:
                            is_callable = callable(attr)
                            has_name = hasattr(attr, 'name')
                            has_description = hasattr(attr, 'description')
                            is_class = isinstance(attr, type)

                            # Only register objects that are not classes, have name and description, and are either callable or have a _run method
                            if not is_class and has_name and has_description and attr_name != 'tool' and (is_callable or hasattr(attr, '_run')):
                                self.register_tool(attr)
                        except TypeError:
                            continue
                except Exception as e:
                    self.logger.error(f"Failed to load tool module {module_name}: {e}")
        self.logger.info(f"Registered regular tools: {[tool.name for tool in self.tools.values()]}")

    
    async def load_mcp_tools(self) -> None:
        """Load MCP tools from the mcp_tools module"""
        try:
            from app.tools.mcp_tools import mcp_client

            # Create MCP tool instances
            mcp_tools = await mcp_client.get_tools()

            # Register MCP tools
            for mcp_tool in mcp_tools:
                try:
                    # Mark as MCP tool
                    setattr(mcp_tool, 'is_mcp', True)
                    self.register_tool(mcp_tool)
                except Exception as e:
                    self.logger.error(f"Failed to register MCP tool {getattr(mcp_tool, 'name', 'unknown')}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to load MCP tools: {e}")
        # Filter and list only MCP tools
        mcp_tool_names = [tool.name for tool in self.tools.values() if getattr(tool, 'is_mcp', False)]
        self.logger.info(f"Registered MCP tools: {mcp_tool_names}")
