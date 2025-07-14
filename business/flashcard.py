from ai_services.prompts import load_prompt
from ai_services.ai_deepseek import DeepseekAIService
from utils.logger import get_logger
import json

class FlashcardBusiness:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service or DeepseekAIService()
        self.logger = get_logger(name="business.flashcard")
        self.logger.info("初始化 FlashcardBusiness")

    def analyze_catalog(self, topic, lang="zh"):
        """
        目录分析，返回AI结构化目录内容。
        """
        self.logger.info(f"开始分析目录: topic={topic}, lang={lang}")
        prompt_template = load_prompt("catalog_analysis", lang)["prompt"]
        prompt = prompt_template.replace("[TOPIC]", topic).replace("{language}", lang)
        
        self.logger.debug(f"调用AI服务: prompt长度={len(prompt)}")
        ai_result = self.ai_service.chat(prompt)
        
        try:
            result = json.loads(ai_result)
            self.logger.info(f"目录分析成功: 获取到{len(result)}个章节")
            return result
        except Exception as e:
            self.logger.warning(f"目录解析JSON失败: {str(e)}")
            return ai_result  # 返回原始内容，便于调试

    def generate_flashcards(self, card_type, topic, number=10, lang="zh"):
        """
        生成指定类型的闪卡，返回结构化内容。
        card_type: basic_card | cloze_card | multiple_choice_card
        """
        self.logger.info(f"开始生成闪卡: card_type={card_type}, topic={topic}, number={number}, lang={lang}")
        prompt_template = load_prompt(card_type, lang)["prompt"]
        prompt = prompt_template.replace("[TOPIC]", topic).replace("[NUMBER]", str(number)).replace("{language}", lang)
        
        self.logger.debug(f"调用AI服务: prompt长度={len(prompt)}")
        ai_result = self.ai_service.chat(prompt)
        
        try:
            result = json.loads(ai_result)
            self.logger.info(f"闪卡生成成功: 获取到{len(result)}张闪卡")
            return result
        except Exception as e:
            self.logger.warning(f"闪卡解析JSON失败: {str(e)}")
            return ai_result  # 返回原始内容，便于调试 