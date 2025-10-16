"""
闪卡数据库操作类

负责 flashcard 表的数据库操作
"""

from typing import Optional, Dict, List, Any
from supabase_service.database import DatabaseService
from business.database.flashcard_result_db import FlashcardResultDB
from utils.logger import get_logger

logger = get_logger(name="business.database.flashcard_db")


class FlashcardDB:
    """闪卡数据库操作类"""

    def __init__(self):
        """初始化闪卡数据库操作类"""
        self.db = DatabaseService()
        self.result_db = FlashcardResultDB()
        self.logger = logger
        self.table = "flashcard"

    def create_flashcard(
        self,
        result_id: str,
        user_id: str,
        card_type: str,
        card_data: Dict[str, Any],
        order_index: int,
        catalog_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建单张闪卡

        Args:
            result_id: 闪卡结果集ID
            user_id: 用户ID
            card_type: 卡片类型（basic/cloze/multiple_choice）
            card_data: 卡片数据（JSONB格式）
            order_index: 排序索引
            catalog_id: 大纲ID（可选）
            section_id: 章节ID（可选，如 "1.1.2"）
            tags: 标签列表（可选）
            notes: 备注（可选）

        Returns:
            dict: 创建结果
                - success: 是否成功
                - data: 创建的记录（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"创建闪卡: result_id={result_id}, card_type={card_type}, order_index={order_index}")

            # 验证 card_type
            if card_type not in ['basic', 'cloze', 'multiple_choice']:
                self.logger.error(f"无效的 card_type: {card_type}")
                return {
                    "success": False,
                    "error": f"无效的 card_type: {card_type}，必须是 basic/cloze/multiple_choice"
                }

            # 构建插入数据
            insert_data = {
                "result_id": result_id,
                "user_id": user_id,
                "card_type": card_type,
                "card_data": card_data,
                "order_index": order_index,
                "is_deleted": False
            }

            # 添加可选字段
            if catalog_id:
                insert_data["catalog_id"] = catalog_id
            if section_id:
                insert_data["section_id"] = section_id
            if tags:
                insert_data["tags"] = tags
            if notes:
                insert_data["notes"] = notes

            # 执行插入
            result = self.db.insert(table=self.table, data=insert_data)

            if result['success']:
                self.logger.info(f"闪卡创建成功: result_id={result_id}, card_id={result['data'].get('id')}")
            else:
                self.logger.error(f"闪卡创建失败: result_id={result_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"创建闪卡异常: result_id={result_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def batch_create_flashcards(
        self,
        result_id: str,
        user_id: str,
        flashcards: List[Dict[str, Any]],
        catalog_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        批量创建闪卡

        Args:
            result_id: 闪卡结果集ID
            user_id: 用户ID
            flashcards: 闪卡列表，每个元素包含：
                - card_type: 卡片类型
                - card_data: 卡片数据
                - order_index: 排序索引
                - section_id: 章节ID（可选）
                - tags: 标签（可选）
                - notes: 备注（可选）
            catalog_id: 大纲ID（可选，统一设置）

        Returns:
            dict: 创建结果
                - success: 是否成功
                - data: 创建的记录列表（成功时）
                - count: 创建数量（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"批量创建闪卡: result_id={result_id}, count={len(flashcards)}")

            # 验证闪卡数据
            for idx, card in enumerate(flashcards):
                if 'card_type' not in card:
                    return {
                        "success": False,
                        "error": f"闪卡 {idx} 缺少 card_type 字段"
                    }
                if card['card_type'] not in ['basic', 'cloze', 'multiple_choice']:
                    return {
                        "success": False,
                        "error": f"闪卡 {idx} 的 card_type 无效: {card['card_type']}"
                    }
                if 'card_data' not in card:
                    return {
                        "success": False,
                        "error": f"闪卡 {idx} 缺少 card_data 字段"
                    }
                if 'order_index' not in card:
                    return {
                        "success": False,
                        "error": f"闪卡 {idx} 缺少 order_index 字段"
                    }

            # 构建批量插入数据
            insert_list = []
            for card in flashcards:
                insert_data = {
                    "result_id": result_id,
                    "user_id": user_id,
                    "card_type": card['card_type'],
                    "card_data": card['card_data'],
                    "order_index": card['order_index'],
                    "is_deleted": False
                }

                # 添加可选字段
                if catalog_id:
                    insert_data["catalog_id"] = catalog_id
                if 'section_id' in card:
                    insert_data["section_id"] = card['section_id']
                if 'tags' in card:
                    insert_data["tags"] = card['tags']
                if 'notes' in card:
                    insert_data["notes"] = card['notes']

                insert_list.append(insert_data)

            # 执行批量插入
            result = self.db.insert(table=self.table, data=insert_list)

            if result['success']:
                self.logger.info(f"批量创建闪卡成功: result_id={result_id}, count={len(flashcards)}")
            else:
                self.logger.error(f"批量创建闪卡失败: result_id={result_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"批量创建闪卡异常: result_id={result_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_flashcards_by_task_id(self, task_id: str) -> Dict[str, Any]:
        """
        根据任务ID查询闪卡列表
        
        实现步骤：
        1. 通过 task_id 在 flashcard_result 表中查询 result_id
        2. 使用 result_id 在 flashcard 表中查询所有未删除的闪卡
        3. 按 order_index 排序返回
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 查询结果
                - success: 是否成功
                - data: 闪卡列表（成功时），按 order_index 排序
                - count: 闪卡数量（成功时）
                - result_id: 闪卡结果ID（成功时）
                - error: 错误信息（失败时）
        """
        try:
            self.logger.info(f"根据任务ID查询闪卡: task_id={task_id}")
            
            # 步骤1: 根据 task_id 查询 flashcard_result 表获取 result_id
            result_query = self.result_db.get_result_by_task_id(task_id)
            
            if not result_query['success']:
                self.logger.warning(f"未找到任务对应的闪卡结果: task_id={task_id}")
                return {
                    "success": False,
                    "error": f"未找到任务对应的闪卡结果: {result_query.get('error', '未知错误')}"
                }
            
            result_data = result_query['data']
            result_id = result_data.get('id')
            
            self.logger.info(f"找到闪卡结果: task_id={task_id}, result_id={result_id}")
            
            # 步骤2: 使用 result_id 查询 flashcard 表中所有未删除的闪卡
            flashcards_result = self.db.select(
                table=self.table,
                filters={"result_id": result_id, "is_deleted": False},
                order_by="order_index"  # 按 order_index 升序排序
            )
            
            if flashcards_result['success']:
                self.logger.info(
                    f"查询闪卡成功: task_id={task_id}, result_id={result_id}, "
                    f"count={flashcards_result['count']}"
                )
                return {
                    "success": True,
                    "data": flashcards_result['data'],
                    "count": flashcards_result['count'],
                    "result_id": result_id
                }
            else:
                self.logger.error(
                    f"查询闪卡失败: task_id={task_id}, result_id={result_id}, "
                    f"错误: {flashcards_result.get('error')}"
                )
                return {
                    "success": False,
                    "error": f"查询闪卡失败: {flashcards_result.get('error')}"
                }
                
        except Exception as e:
            self.logger.error(f"根据任务ID查询闪卡异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
