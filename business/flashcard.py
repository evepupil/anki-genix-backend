from ai_services.workflows import CatalogAnalysisWorkflow, FlashcardGenerateWorkflow
from utils.logger import get_logger

class FlashcardBusiness:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.logger = get_logger(name="business.flashcard")
        self.logger.info("初始化 FlashcardBusiness")

    def analyze_catalog(self, topic, lang="zh"):
        """
        目录分析，返回AI结构化目录内容。
        """
        self.logger.info(f"开始分析目录: topic={topic}, lang={lang}")
        workflow = CatalogAnalysisWorkflow(ai_service=self.ai_service)
        params = {"TOPIC": topic, "lang": lang}
        result = workflow.run(params)
        if isinstance(result, list):
            self.logger.info(f"目录分析成功: 获取到{len(result)}个章节")
        else:
            self.logger.warning(f"目录分析返回非结构化内容: {result}")
        return result

    def generate_flashcards(self, card_type, topic, number=10, lang="zh"):
        """
        生成指定类型的闪卡，返回结构化内容。
        card_type: basic_card | cloze_card | multiple_choice_card
        """
        self.logger.info(f"开始生成闪卡: card_type={card_type}, topic={topic}, number={number}, lang={lang}")
        workflow = FlashcardGenerateWorkflow(card_type=card_type, ai_service=self.ai_service)
        params = {"TOPIC": topic, "NUMBER": number, "lang": lang}
        result = workflow.run(params)
        if isinstance(result, list):
            self.logger.info(f"闪卡生成成功: 获取到{len(result)}张闪卡")
        else:
            self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
        return result

    def generate_flashcards_from_text(self, text_content):
        """
        根据文本内容生成闪卡列表。

        Args:
            text_content: 输入的文本内容

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文本生成闪卡，文本长度: {len(text_content) if text_content else 0}")

        if not text_content or not text_content.strip():
            self.logger.error("文本内容为空")
            return {
                "success": False,
                "error": "文本内容不能为空",
                "cards": []
            }

        try:
            # 使用基础卡片类型生成闪卡
            workflow = FlashcardGenerateWorkflow(card_type="basic_card", ai_service=self.ai_service)

            # 构建参数 - 将文本内容作为主题
            params = {
                "TOPIC": text_content,
                "NUMBER": 10,  # 默认生成10张
                "lang": "zh"
            }

            result = workflow.run(params)

            if isinstance(result, list):
                self.logger.info(f"文本闪卡生成成功: 获取到{len(result)}张闪卡")
                return {
                    "success": True,
                    "cards": result
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"文本闪卡生成失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "cards": []
            } 