"""
大纲数据库操作类

负责 catalog_info 表的数据库操作
"""

from typing import Optional, Dict, List, Any
from supabase_service.database import DatabaseService
from utils.logger import get_logger

logger = get_logger(name="business.database.catalog_db")


class CatalogDB:
    """大纲数据库操作类"""

    def __init__(self):
        """初始化大纲数据库操作类"""
        self.db = DatabaseService()
        self.logger = logger
        self.table = "catalog_info"

    def _generate_catalog_ids(self, catalog_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        为大纲数据生成ID

        Args:
            catalog_data: 大纲数据列表

        Returns:
            添加了ID的大纲数据列表
        """
        result = []

        for chapter_idx, chapter in enumerate(catalog_data, 1):
            # 生成章节ID
            chapter_id = str(chapter_idx)
            chapter_copy = chapter.copy()
            chapter_copy['id'] = chapter_id

            # 处理sections
            if 'sections' in chapter_copy and chapter_copy['sections']:
                sections_with_id = []
                for section_idx, section in enumerate(chapter_copy['sections'], 1):
                    section_id = f"{chapter_id}.{section_idx}"
                    section_copy = section.copy()
                    section_copy['id'] = section_id

                    # 处理subsections
                    if 'subsections' in section_copy and section_copy['subsections']:
                        subsections_with_id = []
                        for subsection_idx, subsection in enumerate(section_copy['subsections'], 1):
                            subsection_id = f"{section_id}.{subsection_idx}"
                            subsection_copy = subsection.copy()
                            subsection_copy['id'] = subsection_id
                            subsections_with_id.append(subsection_copy)
                        section_copy['subsections'] = subsections_with_id

                    sections_with_id.append(section_copy)
                chapter_copy['sections'] = sections_with_id

            result.append(chapter_copy)

        return result

    def create_catalog(
        self,
        task_id: str,
        user_id: str,
        catalog_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        创建大纲记录

        Args:
            task_id: 任务ID
            user_id: 用户ID
            catalog_data: 大纲数据（将自动添加ID）

        Returns:
            dict: 创建结果
                - success: 是否成功
                - data: 创建的记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"创建大纲记录: task_id={task_id}, user_id={user_id}")

            # 为大纲数据生成ID
            catalog_with_ids = self._generate_catalog_ids(catalog_data)
            self.logger.info(f"为大纲数据生成ID完成，章节数: {len(catalog_with_ids)}")

            # 构建插入数据
            insert_data = {
                "task_id": task_id,
                "user_id": user_id,
                "catalog_data": catalog_with_ids,
                "selected": []  # 初始化为空数组
            }

            # 执行插入
            result = self.db.insert(table=self.table, data=insert_data)

            if result['success']:
                self.logger.info(f"大纲记录创建成功: task_id={task_id}, catalog_id={result['data'].get('id')}")
            else:
                self.logger.error(f"大纲记录创建失败: task_id={task_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"创建大纲记录异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_catalog_by_task_id(self, task_id: str) -> Dict[str, Any]:
        """
        根据任务ID获取大纲记录

        Args:
            task_id: 任务ID

        Returns:
            dict: 查询结果
                - success: 是否成功
                - data: 大纲记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"查询大纲记录: task_id={task_id}")

            result = self.db.select(
                table=self.table,
                filters={"task_id": task_id}
            )

            if result['success']:
                if result['count'] > 0:
                    self.logger.info(f"大纲记录查询成功: task_id={task_id}")
                    return {
                        "success": True,
                        "data": result['data'][0]
                    }
                else:
                    self.logger.warning(f"未找到大纲记录: task_id={task_id}")
                    return {
                        "success": False,
                        "error": "未找到大纲记录"
                    }
            else:
                self.logger.error(f"大纲记录查询失败: task_id={task_id}, 错误: {result.get('error')}")
                return result

        except Exception as e:
            self.logger.error(f"查询大纲记录异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def update_selected_sections(
        self,
        task_id: str,
        selected_ids: List[str]
    ) -> Dict[str, Any]:
        """
        更新用户选中的章节ID列表

        Args:
            task_id: 任务ID
            selected_ids: 选中的章节ID列表，如 ['1', '1.1', '2.3.1']

        Returns:
            dict: 更新结果
                - success: 是否成功
                - data: 更新后的记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"更新选中章节: task_id={task_id}, selected_ids={selected_ids}")

            result = self.db.update(
                table=self.table,
                data={"selected": selected_ids},
                filters={"task_id": task_id}
            )

            if result['success']:
                self.logger.info(f"选中章节更新成功: task_id={task_id}")
            else:
                self.logger.error(f"选中章节更新失败: task_id={task_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"更新选中章节异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def delete_catalog_by_task_id(self, task_id: str) -> Dict[str, Any]:
        """
        删除大纲记录（根据任务ID）

        Args:
            task_id: 任务ID

        Returns:
            dict: 删除结果
                - success: 是否成功
                - count: 删除数量（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"删除大纲记录: task_id={task_id}")

            result = self.db.delete(
                table=self.table,
                filters={"task_id": task_id}
            )

            if result['success']:
                self.logger.info(f"大纲记录删除成功: task_id={task_id}, count={result.get('count')}")
            else:
                self.logger.error(f"大纲记录删除失败: task_id={task_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"删除大纲记录异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
