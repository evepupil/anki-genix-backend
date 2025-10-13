"""
Supabase 客户端封装

提供统一的 Supabase 数据库和认证服务接口
"""

import os
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
from utils.logger import get_logger

logger = get_logger(name="supabase.client")


class SupabaseClient:
    """Supabase 客户端类"""

    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化 Supabase 客户端"""
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        """初始化 Supabase 连接"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            if not supabase_url or not supabase_key:
                logger.warning("Supabase 配置缺失，跳过初始化")
                return

            self._client = create_client(supabase_url, supabase_key)
            logger.info(f"Supabase 客户端初始化成功: {supabase_url}")

        except Exception as e:
            logger.error(f"Supabase 客户端初始化失败: {str(e)}", exc_info=True)
            self._client = None

    @property
    def client(self) -> Optional[Client]:
        """获取 Supabase 客户端实例"""
        return self._client

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._client is not None


# 创建全局单例
supabase_client = SupabaseClient()
