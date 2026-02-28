from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SearchEngine(ABC):
    """搜索引擎抽象基类"""
    
    @abstractmethod
    def search(self, query: str) -> str:
        """执行搜索并返回结果
        
        Args:
            query: 搜索查询字符串
            
        Returns:
            格式化的搜索结果字符串
        """
        pass
