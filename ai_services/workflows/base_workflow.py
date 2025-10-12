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
        """
        构建提示词

        参数:
            params: 提示词参数字典，包含：
                - lang: 语言 (zh, en, ja)
                - form: 输入形式 (text, file) - 仅用于闪卡生成
                - mode: 生成模式 (topic, full, section) - 仅用于闪卡生成
                - 其他动态占位符参数 (如 TOPIC, TEXT_CONTENT, SECTION_TITLE, FILENAME 等)

        返回:
            填充好参数的提示词字符串
        """
        lang = params.get("lang", "zh")
        form = getattr(self, 'form', params.get('form', 'text'))
        mode = getattr(self, 'mode', params.get('mode', 'topic'))

        # 加载提示词模板
        prompt_template = load_prompt(self.prompt_key, lang, form, mode)["prompt"]

        # 替换占位符，格式为 [KEY]
        prompt = prompt_template
        for k, v in params.items():
            if k not in ["lang", "form", "mode"]:  # 跳过这些元参数
                placeholder = f"[{k}]"
                prompt = prompt.replace(placeholder, str(v))

        # 替换 {lang} 占位符
        prompt = prompt.replace("{lang}", lang)

        self.logger.debug(f"构建Prompt: {prompt}")
        return prompt

    def parse_result(self, ai_result: str):
        self.logger.debug(f"AI原始返回: {ai_result}")

        # 清理AI返回的内容，去除markdown代码块标记
        cleaned_result = ai_result.strip()
        if cleaned_result.startswith("正在分析"):
            cleaned_result = cleaned_result[4:]  # 移除 ```json
        # 移除 ```json 和 ``` 标记
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]  # 移除 ```json
        elif cleaned_result.startswith("```"):
            cleaned_result = cleaned_result[3:]  # 移除 ```

        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]  # 移除结尾的 ```

        cleaned_result = cleaned_result.strip()

        try:
            result = json.loads(cleaned_result)
            self.logger.info(f"AI返回JSON解析成功: {type(result)}")
            return result
        except Exception as e:
            self.logger.warning(f"AI返回JSON解析失败: {str(e)} | 清理后内容: {cleaned_result[:200]}...")
            return ai_result

    def run(self, params: dict):
        prompt = self.build_prompt(params)
        ai_result = self.ai_service.chat(prompt)
        return self.parse_result(ai_result) 