import json
from ai_services.prompts import load_prompt
from ai_services.ai_base import AIServiceBase
from utils.logger import get_logger

class AIWorkflow:
    prompt_key = None  # 子类需指定

    def __init__(self, ai_service: AIServiceBase = None):
        self.ai_service = ai_service or self.get_default_ai_service()
        self.logger = get_logger(name=f"workflow.{self.__class__.__name__}")

    def get_default_ai_service(self):
        from ai_services.ai_deepseek import DeepseekAIService
        return DeepseekAIService()

    def build_prompt(self, params: dict) -> str:
        lang = params.get("lang", "zh")
        prompt_template = load_prompt(self.prompt_key, lang)["prompt"]
        for k in params:
            prompt = prompt_template.replace(k, str(params[k]))
        self.logger.debug(f"构建Prompt: {prompt}")
        return prompt

    def parse_result(self, ai_result: str):
        self.logger.debug(f"AI原始返回: {ai_result}")
        try:
            result = json.loads(ai_result)
            self.logger.info(f"AI返回JSON解析成功: {type(result)}")
            return result
        except Exception as e:
            self.logger.warning(f"AI返回JSON解析失败: {str(e)} | 原始内容: {ai_result}")
            return ai_result

    def run(self, params: dict):
        prompt = self.build_prompt(params)
        ai_result = self.ai_service.chat(prompt)
        return self.parse_result(ai_result) 