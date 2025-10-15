"""
数据库操作模块

提供各个业务表的数据库操作类
"""

from .catalog_db import CatalogDB
from .flashcard_db import FlashcardDB

__all__ = ['CatalogDB', 'FlashcardDB']
