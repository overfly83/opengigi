from app.tools.search.search_base import SearchEngine
from config.settings import settings
import requests


class SerperSearch(SearchEngine):
    """Serper搜索引擎实现"""
    
    def __init__(self):
        """初始化Serper客户端"""
        self.api_key = settings.SERPER_API_KEY
        if not self.api_key:
            raise ValueError("SERPER_API_KEY is not set in settings")
        self.base_url = "https://google.serper.dev/search"
    
    def search(self, query: str) -> str:
        """执行搜索并返回结果
        
        Args:
            query: 搜索查询字符串
            
        Returns:
            格式化的搜索结果字符串
        """
        # 构建请求参数
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "q": query
        }
        
        # 执行搜索
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()  # 检查请求是否成功
        results = response.json()
        
        # 格式化结果
        formatted_results = []
        
        # 处理有机搜索结果
        if "organic" in results:
            for i, result in enumerate(results["organic"][:3], 1):
                title = result.get("title", "")
                url = result.get("link", "")
                snippet = result.get("snippet", "")
                formatted_results.append(f"{i}. {title}\n{url}\n{snippet[:500]}...\n")
        
        # 如果没有有机结果，尝试获取其他类型的结果
        elif "answerBox" in results:
            answer_box = results["answerBox"]
            title = answer_box.get("title", "")
            url = answer_box.get("link", "")
            snippet = answer_box.get("snippet", "") or answer_box.get("answer", "")
            formatted_results.append(f"1. {title}\n{url}\n{snippet[:500]}...\n")
        
        # 如果没有结果，返回提示
        if not formatted_results:
            return "No search results found."
        
        return "\n".join(formatted_results)
