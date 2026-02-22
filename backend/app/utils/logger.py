import logging
import sys
from typing import Optional
import os

# 颜色代码
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

class CustomLogger(logging.Logger):
    """自定义日志类，支持颜色和源信息"""
    
    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        
        # 配置格式
        formatter = CustomFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        super().debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        super().info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        super().warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        super().error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        super().critical(message, **kwargs)

class CustomFormatter(logging.Formatter):
    """自定义格式器，支持颜色"""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BRIGHT_RED
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # 获取级别颜色
        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        
        # 格式化日志
        log_message = super().format(record)
        
        # 添加颜色
        colored_message = f"{level_color}{log_message}{Colors.RESET}"
        
        return colored_message

def get_logger(name: str, level: int = logging.INFO) -> CustomLogger:
    """获取自定义日志实例"""
    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    return logger

# 示例用法
if __name__ == '__main__':
    logger = get_logger('main_agent')
    
    logger.debug('调试信息')
    logger.info('普通信息')
    logger.warning('警告信息')
    logger.error('错误信息')
    logger.critical('严重错误')