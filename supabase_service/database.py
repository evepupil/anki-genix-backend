"""
Supabase 数据库服务

提供通用的数据库操作接口（CRUD）
职责：仅负责数据库操作，不处理认证逻辑
"""

from typing import Optional, Dict, List, Any
from supabase_service import supabase_client
from utils.logger import get_logger

logger = get_logger(name="supabase.database")


class DatabaseService:
    """数据库操作服务类"""

    def __init__(self):
        """初始化数据库服务"""
        self.client = supabase_client.client
        self.logger = logger

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        查询数据

        Args:
            table: 表名
            columns: 要查询的列，默认"*"查询所有列
            filters: 过滤条件字典，如 {"user_id": "xxx", "status": "pending"}
            order_by: 排序字段，如 "created_at" 或 "created_at.desc"
            limit: 限制返回数量

        Returns:
            dict: 查询结果
                - success: 是否成功
                - data: 数据列表（成功时）
                - count: 数据数量（成功时）
                - error: 错误信息（失败时）
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase 客户端未初始化"
            }

        try:
            self.logger.info(f"查询数据: table={table}, columns={columns}, filters={filters}")

            # 构建查询
            query = self.client.table(table).select(columns)

            # 添加过滤条件
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            # 添加排序
            if order_by:
                if order_by.endswith('.desc'):
                    field = order_by[:-5]
                    query = query.order(field, desc=True)
                elif order_by.endswith('.asc'):
                    field = order_by[:-4]
                    query = query.order(field, desc=False)
                else:
                    query = query.order(order_by)

            # 添加限制
            if limit:
                query = query.limit(limit)

            # 执行查询
            response = query.execute()

            self.logger.info(f"查询成功: table={table}, count={len(response.data)}")
            return {
                "success": True,
                "data": response.data,
                "count": len(response.data)
            }

        except Exception as e:
            self.logger.error(f"查询失败: table={table}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        插入单条数据

        Args:
            table: 表名
            data: 要插入的数据字典

        Returns:
            dict: 插入结果
                - success: 是否成功
                - data: 插入的数据（成功时）
                - error: 错误信息（失败时）
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase 客户端未初始化"
            }

        try:
            self.logger.info(f"插入数据: table={table}, data={data}")

            # 执行插入
            response = self.client.table(table).insert(data).execute()

            self.logger.info(f"插入成功: table={table}")
            return {
                "success": True,
                "data": response.data[0] if response.data else None
            }

        except Exception as e:
            self.logger.error(f"插入失败: table={table}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量插入数据

        Args:
            table: 表名
            data_list: 要插入的数据列表

        Returns:
            dict: 插入结果
                - success: 是否成功
                - data: 插入的数据列表（成功时）
                - count: 插入数量（成功时）
                - error: 错误信息（失败时）
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase 客户端未初始化"
            }

        try:
            self.logger.info(f"批量插入数据: table={table}, count={len(data_list)}")

            # 执行批量插入
            response = self.client.table(table).insert(data_list).execute()

            self.logger.info(f"批量插入成功: table={table}, count={len(response.data)}")
            return {
                "success": True,
                "data": response.data,
                "count": len(response.data)
            }

        except Exception as e:
            self.logger.error(f"批量插入失败: table={table}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新数据

        Args:
            table: 表名
            data: 要更新的数据字典
            filters: 过滤条件字典，如 {"id": "xxx"}

        Returns:
            dict: 更新结果
                - success: 是否成功
                - data: 更新后的数据列表（成功时）
                - count: 更新数量（成功时）
                - error: 错误信息（失败时）
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase 客户端未初始化"
            }

        try:
            self.logger.info(f"更新数据: table={table}, data={data}, filters={filters}")

            # 构建更新查询
            query = self.client.table(table).update(data)

            # 添加过滤条件
            for key, value in filters.items():
                query = query.eq(key, value)

            # 执行更新
            response = query.execute()

            self.logger.info(f"更新成功: table={table}, count={len(response.data)}")
            return {
                "success": True,
                "data": response.data,
                "count": len(response.data)
            }

        except Exception as e:
            self.logger.error(f"更新失败: table={table}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def delete(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        删除数据

        Args:
            table: 表名
            filters: 过滤条件字典，如 {"id": "xxx"}

        Returns:
            dict: 删除结果
                - success: 是否成功
                - count: 删除数量（成功时）
                - error: 错误信息（失败时）
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase 客户端未初始化"
            }

        try:
            self.logger.info(f"删除数据: table={table}, filters={filters}")

            # 构建删除查询
            query = self.client.table(table).delete()

            # 添加过滤条件
            for key, value in filters.items():
                query = query.eq(key, value)

            # 执行删除
            response = query.execute()

            self.logger.info(f"删除成功: table={table}, count={len(response.data)}")
            return {
                "success": True,
                "count": len(response.data)
            }

        except Exception as e:
            self.logger.error(f"删除失败: table={table}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        on_conflict: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        插入或更新数据（如果存在则更新，不存在则插入）

        Args:
            table: 表名
            data: 要插入或更新的数据字典
            on_conflict: 冲突字段，如 "id" 或 "user_id,task_id"

        Returns:
            dict: 操作结果
                - success: 是否成功
                - data: 操作后的数据（成功时）
                - error: 错误信息（失败时）
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase 客户端未初始化"
            }

        try:
            self.logger.info(f"Upsert数据: table={table}, data={data}, on_conflict={on_conflict}")

            # 执行 upsert
            query = self.client.table(table).upsert(data)
            if on_conflict:
                query = query.on_conflict(on_conflict)

            response = query.execute()

            self.logger.info(f"Upsert成功: table={table}")
            return {
                "success": True,
                "data": response.data[0] if response.data else None
            }

        except Exception as e:
            self.logger.error(f"Upsert失败: table={table}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        统计数据数量

        Args:
            table: 表名
            filters: 过滤条件字典（可选）

        Returns:
            dict: 统计结果
                - success: 是否成功
                - count: 数据数量（成功时）
                - error: 错误信息（失败时）
        """
        if not self.client:
            return {
                "success": False,
                "error": "Supabase 客户端未初始化"
            }

        try:
            self.logger.info(f"统计数据: table={table}, filters={filters}")

            # 构建查询（只查询count）
            query = self.client.table(table).select("*", count="exact")

            # 添加过滤条件
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            # 执行查询
            response = query.execute()

            count = response.count if hasattr(response, 'count') else len(response.data)

            self.logger.info(f"统计成功: table={table}, count={count}")
            return {
                "success": True,
                "count": count
            }

        except Exception as e:
            self.logger.error(f"统计失败: table={table}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
