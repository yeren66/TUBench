"""
日志工具模块
"""

import logging
import sys
from config import Config

def setup_logger(name='dataset_builder', level=logging.INFO):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        
    Returns:
        logger: 日志记录器实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level if Config.VERBOSE else logging.WARNING)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件输出
    try:
        file_handler = logging.FileHandler(
            Config.get_output_path(Config.LOG_FILE),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建日志文件: {e}")
    
    return logger

def get_logger(name='dataset_builder'):
    """获取已存在的日志记录器"""
    return logging.getLogger(name)
