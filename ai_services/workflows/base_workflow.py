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
                - NUMBER: 卡片数量（可选）- 如果不提供则使用智能模式
                - 其他动态占位符参数 (如 TOPIC, TEXT_CONTENT, SECTION_TITLE, FILENAME 等)

        返回:
            填充好参数的提示词字符串
        """
        lang = params.get("lang", "zh")
        form = getattr(self, 'form', params.get('form', 'text'))
        mode = getattr(self, 'mode', params.get('mode', 'topic'))

        # 加载提示词模板
        prompt_template = load_prompt(self.prompt_key, lang, form, mode)["prompt"]

        # 处理 NUMBER_INSTRUCTION 占位符（智能数量决策）
        if "[NUMBER_INSTRUCTION]" in prompt_template:
            number_instruction = self._generate_number_instruction(params, lang)
            prompt_template = prompt_template.replace("[NUMBER_INSTRUCTION]", number_instruction)

        # 替换占位符，格式为 [KEY]
        prompt = prompt_template
        for k, v in params.items():
            if k not in ["lang", "form", "mode", "NUMBER"]:  # 跳过这些元参数
                placeholder = f"[{k}]"
                prompt = prompt.replace(placeholder, str(v))

        # 替换 {lang} 占位符
        prompt = prompt.replace("{lang}", lang)

        self.logger.debug(f"构建Prompt: {prompt}")
        return prompt

    def _generate_number_instruction(self, params: dict, lang: str) -> str:
        """
        生成 NUMBER_INSTRUCTION 指令

        如果用户指定了 NUMBER，则生成明确的数量指令
        如果没有指定，则生成智能模式指令，让 AI 自动决定数量

        参数:
            params: 参数字典
            lang: 语言

        返回:
            数量指令字符串
        """
        number = params.get("NUMBER")

        # 判断是否为闪卡生成（通过 prompt_key 判断）
        is_flashcard = self.prompt_key in ["basic_card", "cloze_card", "multiple_choice_card"]

        if number is not None and number > 0:
            # 用户指定了数量 - 明确模式
            if lang == "zh":
                if "basic_card" in str(self.prompt_key):
                    return f"生成{number}组"
                elif "cloze_card" in str(self.prompt_key):
                    return f"生成{number}个"
                elif "multiple_choice_card" in str(self.prompt_key):
                    return f"生成{number}个"
                else:
                    return f"生成{number}个"
            else:  # en
                return f"Generate {number}"
        else:
            # 用户未指定数量 - 智能模式
            if lang == "zh":
                if "basic_card" in str(self.prompt_key):
                    return "分析内容，提取所有值得记忆的知识点，为每个知识点生成一组问答对。生成数量应根据实际内容自然决定（建议5-30组），确保覆盖所有重要知识点"
                elif "cloze_card" in str(self.prompt_key):
                    return "分析内容，提取所有关键术语和概念，为每个术语生成一个填空卡片。生成数量应根据实际内容自然决定（建议5-30个），确保覆盖主要术语"
                elif "multiple_choice_card" in str(self.prompt_key):
                    return "分析内容，提取核心知识点，为每个知识点生成一个多选题。生成数量应根据实际内容自然决定（建议5-30个），确保覆盖关键概念"
                else:
                    return "根据内容实际情况，生成适量的结果（建议5-30个）"
            else:  # en
                if "basic_card" in str(self.prompt_key):
                    return "Analyze the content, extract all memorable knowledge points, and generate one question-answer pair for each point. The number should be determined naturally based on actual content (suggested 5-30 pairs), ensuring all important knowledge points are covered"
                elif "cloze_card" in str(self.prompt_key):
                    return "Analyze the content, extract all key terms and concepts, and generate one cloze card for each term. The number should be determined naturally based on actual content (suggested 5-30 cards), ensuring main terms are covered"
                elif "multiple_choice_card" in str(self.prompt_key):
                    return "Analyze the content, extract core knowledge points, and generate one multiple-choice question for each point. The number should be determined naturally based on actual content (suggested 5-30 questions), ensuring key concepts are covered"
                else:
                    return "Generate an appropriate amount based on actual content (suggested 5-30 items)"

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