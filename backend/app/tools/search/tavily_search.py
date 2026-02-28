from app.tools.search.search_base import SearchEngine
from tavily import TavilyClient
from config.settings import settings


class TavilySearch(SearchEngine):
    """Tavily搜索引擎实现"""
    
    def __init__(self):
        """初始化Tavily客户端"""
        self.api_key = settings.TAVILY_API_KEY
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not set in settings")
        self.client = TavilyClient(api_key=self.api_key)
    
    def search(self, query: str) -> str:
        """执行搜索并返回结果
        
        Args:
            query: 搜索查询字符串
            
        Returns:
            格式化的搜索结果字符串
        """
        # 搜索并获取结果
        results = self.client.search(query=query, search_depth='basic', topic='general')
        
        # 格式化结果
        formatted_results = []
        for i, result in enumerate(results['results'][:3], 1):
            formatted_results.append(f"{i}. {result['title']}\n{result['url']}\n{result['content'][:500]}...\n")
        
        return "\n".join(formatted_results)
