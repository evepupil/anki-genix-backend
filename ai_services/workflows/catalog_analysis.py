from .base_workflow import AIWorkflow

class CatalogAnalysisWorkflow(AIWorkflow):
    """
    大纲生成工作流

    支持两种输入形式：text (文本输入), file (文件上传)
    支持两种生成模式：topic (话题模式), full (全文模式)
    """

    def __init__(self, form="text", mode="topic", ai_service=None):
        """
        初始化大纲生成工作流

        参数:
            form: 输入形式 (text: 文本输入, file: 文件上传)
            mode: 生成模式 (topic: 话题模式, full: 全文模式)
            ai_service: AI服务实例
        """
        self.prompt_key = "catalog_analysis"
        self.form = form
        self.mode = mode
        super().__init__(ai_service) 