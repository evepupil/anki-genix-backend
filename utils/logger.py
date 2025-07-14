import os
import logging
import datetime
import sys
from logging.handlers import RotatingFileHandler

class Logger:
    """
    日志工具类，支持控制台输出和文件输出
    """
    # 日志级别映射
    LEVEL_MAP = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    # 日志格式
    LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, name=None, level='info', log_file=None, max_bytes=10*1024*1024, backup_count=5):
        """
        初始化日志工具类
        :param name: 日志名称，默认使用模块名称
        :param level: 日志级别，默认为info
        :param log_file: 日志文件路径，默认为None（不输出到文件）
        :param max_bytes: 单个日志文件最大大小，默认为10MB
        :param backup_count: 备份文件数量，默认为5
        """
        # 如果未指定name，则使用调用者的模块名
        if name is None:
            frame = sys._getframe(1)
            name = frame.f_globals['__name__']
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVEL_MAP.get(level.lower(), logging.INFO))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))
            self.logger.addHandler(console_handler)
            
            # 文件输出
            if log_file:
                # 确保日志目录存在
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                file_handler = RotatingFileHandler(
                    log_file, 
                    maxBytes=max_bytes, 
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))
                self.logger.addHandler(file_handler)

    def debug(self, message, *args, **kwargs):
        """调试级别日志"""
        self.logger.debug(message, *args, **kwargs)
        
    def info(self, message, *args, **kwargs):
        """信息级别日志"""
        self.logger.info(message, *args, **kwargs)
        
    def warning(self, message, *args, **kwargs):
        """警告级别日志"""
        self.logger.warning(message, *args, **kwargs)
        
    def error(self, message, *args, **kwargs):
        """错误级别日志"""
        self.logger.error(message, *args, **kwargs)
        
    def critical(self, message, *args, **kwargs):
        """严重错误级别日志"""
        self.logger.critical(message, *args, **kwargs)
        
    def exception(self, message, *args, **kwargs):
        """异常日志，附带堆栈信息"""
        self.logger.exception(message, *args, **kwargs)


# 创建默认日志实例
default_logger = Logger(name='anki_genix', level='info', log_file='logs/anki_genix.log')


def get_logger(name=None, level=None, log_file=None):
    """
    获取日志实例的便捷方法
    :param name: 日志名称
    :param level: 日志级别
    :param log_file: 日志文件路径
    :return: Logger实例
    """
    if name is None:
        # 获取调用者的模块名
        frame = sys._getframe(1)
        name = frame.f_globals['__name__']
    
    return Logger(name=name, level=level or 'info', log_file=log_file) 