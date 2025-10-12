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

    def analyze_catalog_from_file(self, file_path: str, lang="zh"):
        """
        基于上传文件生成知识大纲

        参数:
            file_path: 文件路径
            lang: 语言 (zh/en/ja)

        返回:
            大纲数据（JSON格式），包含章节层级结构
        """
        self.logger.info(f"开始基于文件生成大纲 - 文件: {file_path}, 语言: {lang}")

        try:
            # 使用 full 模式，file 形式
            workflow = CatalogAnalysisWorkflow(form="file", mode="full", ai_service=self.ai_service)

            # 构建参数
            params = {
                "lang": lang
            }

            # 使用AI服务的 chat_with_files 方法上传文件
            prompt = workflow.build_prompt(params)
            ai_result = self.ai_service.chat_with_files(prompt, [file_path])
            catalog = workflow.parse_result(ai_result)

            self.logger.info(f"大纲生成成功 - 文件: {file_path}")

            return catalog

        except Exception as e:
            self.logger.error(f"大纲生成失败 - 文件: {file_path}, 错误: {str(e)}")
            raise
