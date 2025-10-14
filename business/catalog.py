"""
大纲生成业务逻辑层

提供三种大纲生成方式：
1. 基于话题生成大纲 (analyze_catalog_from_topic)
2. 基于文本生成大纲 (analyze_catalog_from_text)
3. 基于文件生成大纲 (analyze_catalog_from_file)
"""

from ai_services.workflows.catalog_analysis import CatalogAnalysisWorkflow
from ai_services.ai_base import AIServiceBase
from utils.logger import get_logger

logger = get_logger(name="business.catalog")


class CatalogService:
    """大纲生成服务类"""

    def __init__(self, ai_service: AIServiceBase = None):
        """
        初始化大纲生成服务

        参数:
            ai_service: AI服务实例，如果不提供则使用默认服务
        """
        if ai_service is None:
            # 如果没有提供 ai_service，使用默认的 DeepseekAIService
            from ai_services.ai_deepseek import DeepseekAIService
            ai_service = DeepseekAIService()

        self.ai_service = ai_service
        self.logger = logger

    def analyze_catalog_from_topic(self, topic: str, lang="zh"):
        """
        基于话题生成知识大纲

        参数:
            topic: 主题名称，如"Python编程基础"
            lang: 语言 (zh/en/ja)

        返回:
            大纲数据（JSON格式），包含章节层级结构
        """
        self.logger.info(f"开始基于话题生成大纲 - 话题: {topic}, 语言: {lang}")

        try:
            # 使用 topic 模式，text 形式（话题模式与输入形式无关）
            workflow = CatalogAnalysisWorkflow(form="text", mode="topic", ai_service=self.ai_service)

            params = {
                "TOPIC": topic,
                "lang": lang
            }

            catalog = workflow.run(params)
            self.logger.info(f"大纲生成成功 - 话题: {topic}")

            return catalog

        except Exception as e:
            self.logger.error(f"大纲生成失败 - 话题: {topic}, 错误: {str(e)}")
            raise

    def analyze_catalog_from_text(self, text_content: str, lang="zh"):
        """
        基于文本内容生成知识大纲

        参数:
            text_content: 完整的文本内容
            lang: 语言 (zh/en/ja)

        返回:
            大纲数据（JSON格式），包含章节层级结构
        """
        self.logger.info(f"开始基于文本生成大纲 - 文本长度: {len(text_content)}, 语言: {lang}")

        try:
            # 使用 full 模式，text 形式
            workflow = CatalogAnalysisWorkflow(form="text", mode="full", ai_service=self.ai_service)

            params = {
                "TEXT_CONTENT": text_content,
                "lang": lang
            }

            catalog = workflow.run(params)
            self.logger.info(f"大纲生成成功 - 文本长度: {len(text_content)}")

            return catalog

        except Exception as e:
            self.logger.error(f"大纲生成失败 - 文本长度: {len(text_content)}, 错误: {str(e)}")
            raise

    def analyze_catalog_from_file(self, file_path: str, lang="zh", task_id=None):
        """
        基于上传文件生成知识大纲

        参数:
            file_path: 文件路径
            lang: 语言 (zh/en/ja)
            task_id: 任务ID（必填，用于状态追踪）

        返回:
            大纲数据（JSON格式），包含章节层级结构
        """
        self.logger.info(f"开始基于文件生成大纲 - 文件: {file_path}, task_id={task_id}, 语言: {lang}")

        # 必须提供task_id
        if not task_id:
            self.logger.error("task_id未提供")
            raise ValueError("task_id为必填参数")

        # 创建任务管理器
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        try:
            # 1. 更新状态：文件上传中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=file_uploading")
            task_mgr.update_status(task_id, 'file_uploading')

            # 2. 上传文件到AI服务器
            self.logger.info(f"开始上传文件到AI服务器: {file_path}")
            multimedia = self.ai_service.upload_files([file_path])
            self.logger.info(f"文件上传成功，multimedia数量: {len(multimedia)}")

            # 2.1 获取当前任务的input_data
            task = task_mgr.get_task(task_id)
            if task:
                input_data = task.get('input_data', {})
                # 更新input_data.file.info字段，保存multimedia信息
                if 'file' not in input_data:
                    input_data['file'] = {}
                input_data['file']['info'] = multimedia

                self.logger.info(f"保存文件multimedia到input_data.file.info: task_id={task_id}")
                # 使用task_mgr的db来更新
                result = task_mgr.db.update(
                    table="task_info",
                    data={"input_data": input_data},
                    filters={"id": task_id}
                )
                if not result.get('success'):
                    self.logger.error(f"保存multimedia失败: {result.get('error')}")

            # 3. 更新状态：AI处理中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=ai_processing")
            task_mgr.update_status(task_id, 'ai_processing')

            # 4. 更新状态：生成大纲中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=generating_catalog")
            task_mgr.update_status(task_id, 'generating_catalog')

            # 5. 使用 full 模式，file 形式
            workflow = CatalogAnalysisWorkflow(form="file", mode="full", ai_service=self.ai_service)

            # 构建参数
            params = {
                "lang": lang
            }

            # 6. 使用已上传的文件进行对话
            prompt = workflow.build_prompt(params)
            ai_result = self.ai_service.chat_with_multimedia(prompt, multimedia)
            catalog = workflow.parse_result(ai_result)

            self.logger.info(f"大纲生成成功 - 文件: {file_path}")

            # 7. 更新状态：大纲完成，等待用户选择章节
            self.logger.info(f"更新任务状态: task_id={task_id}, status=catalog_ready")
            task_mgr.update_status(task_id, 'catalog_ready')

            return catalog

        except Exception as e:
            self.logger.error(f"大纲生成失败 - 文件: {file_path}, 错误: {str(e)}")
            # 更新任务状态为失败
            task_mgr.update_status(task_id, 'failed')
            raise
