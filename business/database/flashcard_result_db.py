"""
闪卡结果数据库操作类

负责 flashcard_result 表的数据库操作
"""

from typing import Optional, Dict, Any
from supabase_service.database import DatabaseService
from utils.logger import get_logger

logger = get_logger(name="business.database.flashcard_result_db")


class FlashcardResultDB:
    """闪卡结果数据库操作类"""

    def __init__(self):
        """初始化闪卡结果数据库操作类"""
        self.db = DatabaseService()
        self.logger = logger
        self.table = "flashcard_result"

    def create_result(
        self,
        task_id: str,
        user_id: str,
        source_type: str,
        catalog_id: Optional[str] = None,
        total_count: int = 0
    ) -> Dict[str, Any]:
        """
        创建闪卡结果记录

        Args:
            task_id: 任务ID
            user_id: 用户ID
            source_type: 来源类型（text/file/web）
            catalog_id: 大纲ID（可选）
            total_count: 总卡片数量（默认0，后续通过触发器自动维护）

        Returns:
            dict: 创建结果
                - success: 是否成功
                - data: 创建的记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"创建闪卡结果记录: task_id={task_id}, user_id={user_id}, source_type={source_type}")

            # 验证 source_type
            if source_type not in ['text', 'file', 'web']:
                self.logger.error(f"无效的 source_type: {source_type}")
                return {
                    "success": False,
                    "error": f"无效的 source_type: {source_type}，必须是 text/file/web"
                }

            # 构建插入数据
            insert_data = {
                "task_id": task_id,
                "user_id": user_id,
                "source_type": source_type,
                "total_count": total_count,
                "is_exported": False
            }

            # 添加可选字段
            if catalog_id:
                insert_data["catalog_id"] = catalog_id

            # 执行插入
            result = self.db.insert(table=self.table, data=insert_data)

            if result['success']:
                self.logger.info(f"闪卡结果记录创建成功: task_id={task_id}, result_id={result['data'].get('id')}")
            else:
                self.logger.error(f"闪卡结果记录创建失败: task_id={task_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"创建闪卡结果记录异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_result_by_task_id(self, task_id: str) -> Dict[str, Any]:
        """
        根据任务ID获取闪卡结果记录

        Args:
            task_id: 任务ID

        Returns:
            dict: 查询结果
                - success: 是否成功
                - data: 闪卡结果记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"查询闪卡结果记录: task_id={task_id}")

            result = self.db.select(
                table=self.table,
                filters={"task_id": task_id}
            )

            if result['success']:
                if result['count'] > 0:
                    self.logger.info(f"闪卡结果记录查询成功: task_id={task_id}")
                    return {
                        "success": True,
                        "data": result['data'][0]
                    }
                else:
                    self.logger.warning(f"未找到闪卡结果记录: task_id={task_id}")
                    return {
                        "success": False,
                        "error": "未找到闪卡结果记录"
                    }
            else:
                self.logger.error(f"闪卡结果记录查询失败: task_id={task_id}, 错误: {result.get('error')}")
                return result

        except Exception as e:
            self.logger.error(f"查询闪卡结果记录异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_result_by_id(self, result_id: str) -> Dict[str, Any]:
        """
        根据结果ID获取闪卡结果记录

        Args:
            result_id: 闪卡结果ID

        Returns:
            dict: 查询结果
                - success: 是否成功
                - data: 闪卡结果记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"查询闪卡结果记录: result_id={result_id}")

            result = self.db.select(
                table=self.table,
                filters={"id": result_id}
            )

            if result['success']:
                if result['count'] > 0:
                    self.logger.info(f"闪卡结果记录查询成功: result_id={result_id}")
                    return {
                        "success": True,
                        "data": result['data'][0]
                    }
                else:
                    self.logger.warning(f"未找到闪卡结果记录: result_id={result_id}")
                    return {
                        "success": False,
                        "error": "未找到闪卡结果记录"
                    }
            else:
                self.logger.error(f"闪卡结果记录查询失败: result_id={result_id}, 错误: {result.get('error')}")
                return result

        except Exception as e:
            self.logger.error(f"查询闪卡结果记录异常: result_id={result_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_results_by_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
        source_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取用户的闪卡结果列表

        Args:
            user_id: 用户ID
            limit: 限制返回数量（可选）
            source_type: 过滤来源类型（可选，text/file/web）

        Returns:
            dict: 查询结果
                - success: 是否成功
                - data: 闪卡结果列表（成功时）
                - count: 数量（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"查询用户闪卡结果列表: user_id={user_id}, limit={limit}, source_type={source_type}")

            # 构建过滤条件
            filters = {"user_id": user_id}
            if source_type:
                filters["source_type"] = source_type

            result = self.db.select(
                table=self.table,
                filters=filters,
                order_by="created_at.desc",
                limit=limit
            )

            if result['success']:
                self.logger.info(f"用户闪卡结果列表查询成功: user_id={user_id}, count={result['count']}")
            else:
                self.logger.error(f"用户闪卡结果列表查询失败: user_id={user_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"查询用户闪卡结果列表异常: user_id={user_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def update_total_count(self, result_id: str, total_count: int) -> Dict[str, Any]:
        """
        更新总卡片数量

        Args:
            result_id: 闪卡结果ID
            total_count: 新的总卡片数量

        Returns:
            dict: 更新结果
                - success: 是否成功
                - data: 更新后的记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"更新总卡片数量: result_id={result_id}, total_count={total_count}")

            result = self.db.update(
                table=self.table,
                data={"total_count": total_count},
                filters={"id": result_id}
            )

            if result['success']:
                self.logger.info(f"总卡片数量更新成功: result_id={result_id}")
            else:
                self.logger.error(f"总卡片数量更新失败: result_id={result_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"更新总卡片数量异常: result_id={result_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def update_export_info(
        self,
        result_id: str,
        export_format: str,
        resource_url: str
    ) -> Dict[str, Any]:
        """
        更新导出信息

        Args:
            result_id: 闪卡结果ID
            export_format: 导出格式（apkg/csv）
            resource_url: 资源文件下载链接

        Returns:
            dict: 更新结果
                - success: 是否成功
                - data: 更新后的记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"更新导出信息: result_id={result_id}, format={export_format}")

            # 验证 export_format
            if export_format not in ['apkg', 'csv']:
                self.logger.error(f"无效的 export_format: {export_format}")
                return {
                    "success": False,
                    "error": f"无效的 export_format: {export_format}，必须是 apkg/csv"
                }

            # 导入当前时间
            from datetime import datetime

            result = self.db.update(
                table=self.table,
                data={
                    "is_exported": True,
                    "export_format": export_format,
                    "resource_url": resource_url,
                    "exported_at": datetime.utcnow().isoformat()
                },
                filters={"id": result_id}
            )

            if result['success']:
                self.logger.info(f"导出信息更新成功: result_id={result_id}")
            else:
                self.logger.error(f"导出信息更新失败: result_id={result_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"更新导出信息异常: result_id={result_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def delete_result(self, result_id: str) -> Dict[str, Any]:
        """
        删除闪卡结果记录

        Args:
            result_id: 闪卡结果ID

        Returns:
            dict: 删除结果
                - success: 是否成功
                - count: 删除数量（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"删除闪卡结果记录: result_id={result_id}")

            result = self.db.delete(
                table=self.table,
                filters={"id": result_id}
            )

            if result['success']:
                self.logger.info(f"闪卡结果记录删除成功: result_id={result_id}, count={result.get('count')}")
            else:
                self.logger.error(f"闪卡结果记录删除失败: result_id={result_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"删除闪卡结果记录异常: result_id={result_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def count_results_by_source_type(self, user_id: str) -> Dict[str, Any]:
        """
        统计用户各来源类型的闪卡结果数量

        Args:
            user_id: 用户ID

        Returns:
            dict: 统计结果
                - success: 是否成功
                - data: 统计数据（成功时）
                    {
                        "text": 10,
                        "file": 5,
                        "web": 3
                    }
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"统计用户各来源类型闪卡数量: user_id={user_id}")

            # 查询所有记录（只需要 source_type 字段）
            result = self.db.select(
                table=self.table,
                columns="source_type",
                filters={"user_id": user_id}
            )

            if result['success']:
                # 手动统计
                counts = {"text": 0, "file": 0, "web": 0}
                for record in result['data']:
                    source_type = record.get('source_type')
                    if source_type in counts:
                        counts[source_type] += 1

                self.logger.info(f"统计完成: user_id={user_id}, counts={counts}")
                return {
                    "success": True,
                    "data": counts
                }
            else:
                self.logger.error(f"统计失败: user_id={user_id}, 错误: {result.get('error')}")
                return result

        except Exception as e:
            self.logger.error(f"统计异常: user_id={user_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
