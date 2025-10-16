"""
导出业务逻辑

负责处理闪卡导出相关的业务逻辑，支持 CSV 和 APKG 格式导出
"""

import os
from typing import Dict, Any, Optional
from business.database.flashcard_db import FlashcardDB
from utils.anki_exporter import AnkiExporter
from utils.logger import get_logger

logger = get_logger(name="business.export")


class ExportBusiness:
    """导出业务类"""

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化导出业务类

        Args:
            output_dir: 导出文件保存目录，默认为 'exports'
        """
        self.flashcard_db = FlashcardDB()
        self.output_dir = output_dir or 'exports'
        self.anki_exporter = AnkiExporter(output_dir=self.output_dir)
        self.logger = logger

    def export_task_flashcards(
        self,
        task_id: str,
        export_format: str = 'apkg',
        deck_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导出指定任务的闪卡

        Args:
            task_id: 任务ID
            export_format: 导出格式，支持 'apkg' 或 'csv'
            deck_name: 牌组名称（仅用于 apkg 格式，可选）

        Returns:
            dict: 导出结果
                - success: 是否成功
                - file_path: 生成的文件路径（成功时）
                - file_name: 文件名（成功时）
                - format: 导出格式（成功时）
                - count: 导出的卡片数量（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"开始导出任务闪卡: task_id={task_id}, format={export_format}")

            # 验证导出格式
            if export_format not in ['apkg', 'csv']:
                self.logger.error(f"不支持的导出格式: {export_format}")
                return {
                    "success": False,
                    "error": f"不支持的导出格式: {export_format}，仅支持 'apkg' 或 'csv'"
                }

            # 1. 查询任务对应的闪卡数据
            flashcards_result = self.flashcard_db.get_flashcards_by_task_id(task_id)

            if not flashcards_result['success']:
                self.logger.warning(f"查询任务闪卡失败: task_id={task_id}, error={flashcards_result.get('error')}")
                return {
                    "success": False,
                    "error": f"查询任务闪卡失败: {flashcards_result.get('error')}"
                }

            flashcards = flashcards_result['data']
            flashcards_count = flashcards_result['count']

            if flashcards_count == 0:
                self.logger.warning(f"任务没有可导出的闪卡: task_id={task_id}")
                return {
                    "success": False,
                    "error": "该任务没有可导出的闪卡"
                }

            self.logger.info(f"查询到 {flashcards_count} 张闪卡，准备导出")

            # 2. 根据格式导出文件
            if export_format == 'apkg':
                # 使用默认牌组名称或自定义名称
                final_deck_name = deck_name or f"AnkiGenix_{task_id[:8]}"
                file_path = self.anki_exporter.json_to_anki_pkg(final_deck_name, flashcards)
            else:  # csv
                file_path = self.anki_exporter.json_to_csv(flashcards)

            # 3. 检查文件是否生成成功
            if not os.path.exists(file_path):
                self.logger.error(f"文件生成失败: {file_path}")
                return {
                    "success": False,
                    "error": "文件生成失败"
                }

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            self.logger.info(
                f"导出成功: task_id={task_id}, format={export_format}, "
                f"file={file_name}, size={file_size} bytes, count={flashcards_count}"
            )

            return {
                "success": True,
                "file_path": file_path,
                "file_name": file_name,
                "format": export_format,
                "count": flashcards_count,
                "size": file_size
            }

        except Exception as e:
            self.logger.error(f"导出任务闪卡异常: task_id={task_id}, error={str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"导出失败: {str(e)}"
            }

    def export_result_flashcards(
        self,
        result_id: str,
        export_format: str = 'apkg',
        deck_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导出指定结果集的闪卡

        Args:
            result_id: 闪卡结果ID
            export_format: 导出格式，支持 'apkg' 或 'csv'
            deck_name: 牌组名称（仅用于 apkg 格式，可选）

        Returns:
            dict: 导出结果
                - success: 是否成功
                - file_path: 生成的文件路径（成功时）
                - file_name: 文件名（成功时）
                - format: 导出格式（成功时）
                - count: 导出的卡片数量（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"开始导出结果集闪卡: result_id={result_id}, format={export_format}")

            # 验证导出格式
            if export_format not in ['apkg', 'csv']:
                self.logger.error(f"不支持的导出格式: {export_format}")
                return {
                    "success": False,
                    "error": f"不支持的导出格式: {export_format}，仅支持 'apkg' 或 'csv'"
                }

            # 1. 直接查询 result_id 对应的闪卡
            flashcards_result = self.flashcard_db.db.select(
                table="flashcard",
                filters={"result_id": result_id, "is_deleted": False},
                order_by="order_index"
            )

            if not flashcards_result['success']:
                self.logger.warning(f"查询结果集闪卡失败: result_id={result_id}, error={flashcards_result.get('error')}")
                return {
                    "success": False,
                    "error": f"查询结果集闪卡失败: {flashcards_result.get('error')}"
                }

            flashcards = flashcards_result['data']
            flashcards_count = flashcards_result['count']

            if flashcards_count == 0:
                self.logger.warning(f"结果集没有可导出的闪卡: result_id={result_id}")
                return {
                    "success": False,
                    "error": "该结果集没有可导出的闪卡"
                }

            self.logger.info(f"查询到 {flashcards_count} 张闪卡，准备导出")

            # 2. 根据格式导出文件
            if export_format == 'apkg':
                # 使用默认牌组名称或自定义名称
                final_deck_name = deck_name or f"AnkiGenix_{result_id[:8]}"
                file_path = self.anki_exporter.json_to_anki_pkg(final_deck_name, flashcards)
            else:  # csv
                file_path = self.anki_exporter.json_to_csv(flashcards)

            # 3. 检查文件是否生成成功
            if not os.path.exists(file_path):
                self.logger.error(f"文件生成失败: {file_path}")
                return {
                    "success": False,
                    "error": "文件生成失败"
                }

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            self.logger.info(
                f"导出成功: result_id={result_id}, format={export_format}, "
                f"file={file_name}, size={file_size} bytes, count={flashcards_count}"
            )

            return {
                "success": True,
                "file_path": file_path,
                "file_name": file_name,
                "format": export_format,
                "count": flashcards_count,
                "size": file_size
            }

        except Exception as e:
            self.logger.error(f"导出结果集闪卡异常: result_id={result_id}, error={str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"导出失败: {str(e)}"
            }
