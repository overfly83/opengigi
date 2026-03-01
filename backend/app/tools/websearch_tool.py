#!/usr/bin/env python3
import sys
import os
import dotenv
from app.tools import tool
from app.config.settings import settings

dotenv.load_dotenv()

# Add the backend directory to the Python path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class SearchEngineFactory:
    """搜索引擎工厂类"""
    
    @staticmethod
    def create_search_engine() -> object:
        """根据配置创建搜索引擎实例
        
        Returns:
            搜索引擎实例
        """
        provider = settings.SEARCH_PROVIDER.lower()
        
        if provider == "tavily":
            from app.tools.search.tavily_search import TavilySearch
            return TavilySearch()
        elif provider == "serpapi":
            from app.tools.search.serpapi_search import SerpAPISearch
            return SerpAPISearch()
        elif provider == "serper":
            from app.tools.search.serper_search import SerperSearch
            return SerperSearch()
        else:
            raise ValueError(f"Unsupported search provider: {provider}")


@tool
def websearch(query: str) -> str:
    """Search the web for information using the configured search provider.
    
    Args:
        query: The search query string
        
    Returns:
        Search results as a string
    """
    # 创建搜索引擎实例
    search_engine = SearchEngineFactory.create_search_engine()
    
    # 执行搜索并返回结果
    return search_engine.search(query)


if __name__ == "__main__":
    import asyncio
    
    async def test_websearch():
        # Test the websearch tool directly (bypassing the decorator)
        search_engine = SearchEngineFactory.create_search_engine()
        
        # Search and get results
        results = search_engine.search("What is the capital of France?")
        
        print(results)
    
    asyncio.run(test_websearch())
