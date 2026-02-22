#!/usr/bin/env python3
"""
LangChain Tool Registry

This module manages the registration and discovery of LangChain tools.
"""

import importlib
import os
from typing import Dict, List, Callable, Any

class ToolRegistry:
    """Registry for managing LangChain tools"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, tool_func) -> None:
        """Register a new LangChain tool"""
        if hasattr(tool_func, 'name'):
            tool_name = tool_func.name
        elif hasattr(tool_func, '__name__'):
            tool_name = tool_func.__name__
        else:
            raise ValueError(f"Tool object has no name attribute: {tool_func}")
        
        if tool_name in self.tools:
            raise ValueError(f"Tool {tool_name} already registered")
        self.tools[tool_name] = tool_func
    
    def get_tool(self, name: str) -> Callable:
        """Get a registered tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return self.tools[name]
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all registered tools"""
        return [
            {"name": name, "description": getattr(tool, 'description', '')}
            for name, tool in self.tools.items()
        ]

# Global tool registry
tool_registry = ToolRegistry()

def load_tools() -> None:
    """Load all LangChain tools from the tools directory"""
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
                        if not is_class and has_name and has_description and attr_name != 'tool':
                            tool_registry.register_tool(attr)
                    except TypeError:
                        continue
            except Exception as e:
                print(f"Failed to load tool module {module_name}: {e}")

# Load tools on module import
load_tools()