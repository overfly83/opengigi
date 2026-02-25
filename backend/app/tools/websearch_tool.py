#!/usr/bin/env python3
import sys
import os
import dotenv
from app.tools import tool
from tavily import TavilyClient
from config.settings import settings

dotenv.load_dotenv()

# Add the backend directory to the Python path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))




@tool
def websearch(query: str) -> str:
    """Search the web for information using Tavily.
    
    Args:
        query: The search query string
        
    Returns:
        Search results as a string
    """
    # Get Tavily API key from settings
    api_key = settings.TAVILY_API_KEY
    
    # Initialize Tavily client
    tavily = TavilyClient(api_key=api_key)
    
    # Search and get results
    results = tavily.search(query=query, search_depth='basic', topic='general')
    
    # Format results
    formatted_results = []
    for i, result in enumerate(results['results'][:3], 1):
        formatted_results.append(f"{i}. {result['title']}\n{result['url']}\n{result['content'][:200]}...\n")
    
    return "\n".join(formatted_results)


if __name__ == "__main__":
    import asyncio
    
    async def test_websearch():
        # Test the websearch tool directly (bypassing the decorator)
        from tavily import TavilyClient
        
        # Get Tavily API key from settings
        api_key = settings.TAVILY_API_KEY
        
        # Initialize Tavily client
        tavily = TavilyClient(api_key=api_key)
        
        # Search and get results
        results = tavily.search(query="What is the capital of France?", search_depth='basic', topic='general')
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results['results'][:3], 1):
            formatted_results.append(f"{i}. {result['title']}\n{result['url']}\n{result['content'][:200]}...\n")
        
        print("\n".join(formatted_results))
    
    asyncio.run(test_websearch())
