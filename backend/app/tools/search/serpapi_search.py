from app.tools.search.search_base import SearchEngine
from config.settings import settings


class SerpAPISearch(SearchEngine):
    """SerpAPI搜索引擎实现"""
    
    def __init__(self):
        """初始化SerpAPI客户端"""
        self.api_key = settings.SERPAPI_API_KEY
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY is not set in settings")
        
        # 尝试导入serpapi库
        try:
            from serpapi import GoogleSearch
            self.GoogleSearch = GoogleSearch
        except ImportError:
            raise ImportError("serpapi library is not installed. Please run 'pip install serpapi'")
    
    def search(self, query: str) -> str:
        """执行搜索并返回结果
        
        Args:
            query: 搜索查询字符串
            
        Returns:
            格式化的搜索结果字符串
        """
        try:
            # 构建搜索参数
            params = {
                "q": query,
                "api_key": self.api_key
            }
            
            # 执行搜索
            search = self.GoogleSearch(params)
            results = search.get_dict()
            
            # 格式化结果
            formatted_results = []
            
            # 处理有机搜索结果
            if "organic_results" in results:
                for i, result in enumerate(results["organic_results"][:3], 1):
                    title = result.get("title", "")
                    url = result.get("link", "")
                    snippet = result.get("snippet", "")
                    formatted_results.append(f"{i}. {title}\n{url}\n{snippet[:500]}...\n")
            
            # 如果没有有机结果，尝试获取其他类型的结果
            elif "answer_box" in results:
                answer_box = results["answer_box"]
                title = answer_box.get("title", "")
                url = answer_box.get("link", "")
                snippet = answer_box.get("snippet", "") or answer_box.get("answer", "")
                formatted_results.append(f"1. {title}\n{url}\n{snippet[:500]}...\n")
            
            # 如果没有结果，返回提示
            if not formatted_results:
                return "No search results found."
            
            return "\n".join(formatted_results)
        except Exception as e:
            # 捕获所有异常并返回错误信息
            return f"Error during search: {str(e)}"
