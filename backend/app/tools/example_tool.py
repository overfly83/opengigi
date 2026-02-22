#!/usr/bin/env python3
"""
Example LangChain Tool

This is a template for creating new LangChain tools.
"""

from app.tools import tool


@tool
def example_tool(endpoint: str, method: str = "GET", **kwargs) -> dict:
    """An example tool that performs a simple API call
    
    Args:
        endpoint: API endpoint to call
        method: HTTP method (GET, POST, PUT, DELETE)
        **kwargs: Additional parameters
        
    Returns:
        Mock API response
    """
    return {
        "status": "success",
        "endpoint": endpoint,
        "method": method,
        "data": kwargs,
        "message": "Example tool call successful"
    }
