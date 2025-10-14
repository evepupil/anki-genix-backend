"""
任务状态管理器

负责管理任务状态的更新和查询
职责：
1. 更新任务状态
2. 查询任务信息
3. 验证任务合法性
"""

from typing import Optional, Dict, Any
from supabase_service.database import DatabaseService
from utils.logger import get_logger

logger = get_logger(name="business.task_manager")


class TaskManager:
    """任务状态管理器"""

    def __init__(self):
        """初始化任务管理器"""
        self.db = DatabaseService()
        self.logger = logger

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务信息

        Args:
            task_id: 任务ID

        Returns:
            dict: 任务信息，如果不存在则返回 None
        """
        try:
            self.logger.info(f"查询任务信息: task_id={task_id}")

            result = self.db.select(
                table="task_info",
                filters={"id": task_id}
            )

            if result['success'] and result['count'] > 0:
                task = result['data'][0]
                self.logger.info(f"任务查询成功: task_id={task_id}, status={task.get('status')}")
                return task
            else:
                self.logger.warning(f"任务不存在: task_id={task_id}")
                return None

        except Exception as e:
            self.logger.error(f"查询任务失败: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return None

    def update_status(
        self,
        task_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态

        Returns:
            dict: 更新结果
                - success: 是否成功
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"更新任务状态: task_id={task_id}, status={status}")

            # 构建更新数据（只更新状态）
            update_data = {"status": status}

            # 执行更新
            result = self.db.update(
                table="task_info",
                data=update_data,
                filters={"id": task_id}
            )

            if result['success']:
                self.logger.info(f"任务状态更新成功: task_id={task_id}, status={status}")
            else:
                self.logger.error(f"任务状态更新失败: task_id={task_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"更新任务状态异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def update_input_data_field(
        self,
        task_id: str,
        field_name: str,
        field_value: Any
    ) -> Dict[str, Any]:
        """
        更新任务input_data中的某个字段

        Args:
            task_id: 任务ID
            field_name: 字段名
            field_value: 字段值

        Returns:
            dict: 更新结果
                - success: 是否成功
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"更新任务input_data字段: task_id={task_id}, field={field_name}")

            # 先获取当前任务
            task = self.get_task(task_id)
            if not task:
                return {
                    "success": False,
                    "error": "任务不存在"
                }

            # 获取当前的input_data
            input_data = task.get('input_data', {})
            if input_data is None:
                input_data = {}

            # 更新字段
            input_data[field_name] = field_value

            # 执行更新
            result = self.db.update(
                table="task_info",
                data={"input_data": input_data},
                filters={"id": task_id}
            )

            if result['success']:
                self.logger.info(f"input_data字段更新成功: task_id={task_id}, field={field_name}")
            else:
                self.logger.error(f"input_data字段更新失败: task_id={task_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"更新input_data字段异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def validate_task(
        self,
        task_id: str,
        expected_task_type: Optional[str] = None,
        expected_workflow_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        验证任务是否合法

        Args:
            task_id: 任务ID
            expected_task_type: 期望的任务类型（可选），如 "text", "file", "web", "topic"
            expected_workflow_type: 期望的工作流类型（可选），如 "extract_catalog", "direct_generate"

        Returns:
            dict: 验证结果
                - valid: 是否合法
                - task: 任务信息（合法时）
                - error: 错误信息（不合法时）
        """
        try:
            # 1. 查询任务
            task = self.get_task(task_id)
            if not task:
                return {
                    "valid": False,
                    "error": "任务不存在"
                }

            # 2. 验证任务类型（输入类型）
            if expected_task_type and task.get('task_type') != expected_task_type:
                return {
                    "valid": False,
                    "error": f"任务类型不匹配，期望: {expected_task_type}, 实际: {task.get('task_type')}"
                }

            # 3. 验证工作流类型
            if expected_workflow_type and task.get('workflow_type') != expected_workflow_type:
                return {
                    "valid": False,
                    "error": f"工作流类型不匹配，期望: {expected_workflow_type}, 实际: {task.get('workflow_type')}"
                }

            # 4. 验证任务状态（不应该是 completed 或 failed）
            current_status = task.get('status')
            if current_status in ['completed', 'failed']:
                return {
                    "valid": False,
                    "error": f"任务已结束，当前状态: {current_status}"
                }

            self.logger.info(f"任务验证通过: task_id={task_id}")
            return {
                "valid": True,
                "task": task
            }

        except Exception as e:
            self.logger.error(f"任务验证异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "valid": False,
                "error": str(e)
            }
