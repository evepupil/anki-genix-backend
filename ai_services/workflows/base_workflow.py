import json
from ai_services.prompts import load_prompt
from ai_services.ai_base import AIServiceBase

class AIWorkflow:
    prompt_key = None  # 子类需指定

    def __init__(self, ai_service: AIServiceBase = None):
        self.ai_service = ai_service or self.get_default_ai_service()

    def get_default_ai_service(self):
        from ai_services.ai_deepseek import DeepseekAIService
        return DeepseekAIService()

    def build_prompt(self, params: dict) -> str:
        lang = params.get("lang", "zh")
        prompt_template = load_prompt(self.prompt_key, lang)["prompt"]
        return prompt_template.format(**params)

    def parse_result(self, ai_result: str):
        try:
            return json.loads(ai_result)
        except Exception:
            return ai_result

    def run(self, params: dict):
        prompt = self.build_prompt(params)
        ai_result = self.ai_service.chat(prompt)
        return self.parse_result(ai_result) 