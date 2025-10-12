from .base_workflow import AIWorkflow

class FlashcardGenerateWorkflow(AIWorkflow):
    """
    闪卡生成工作流

    支持三种卡片类型：basic_card, cloze_card, multiple_choice_card
    支持两种输入形式：text (文本输入), file (文件上传)
    支持三种生成模式：topic (话题模式), full (全文模式), section (章节模式)
    """

    def __init__(self, card_type="basic_card", form="text", mode="topic", ai_service=None):
        """
        初始化闪卡生成工作流

        参数:
            card_type: 卡片类型 (basic_card, cloze_card, multiple_choice_card)
            form: 输入形式 (text: 文本输入, file: 文件上传)
            mode: 生成模式 (topic: 话题模式, full: 全文模式, section: 章节模式)
            ai_service: AI服务实例
        """
        self.prompt_key = card_type
        self.form = form
        self.mode = mode
        super().__init__(ai_service) 