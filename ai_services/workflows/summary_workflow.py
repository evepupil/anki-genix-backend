from .base_workflow import AIWorkflow
import re

class SummaryWorkflow(AIWorkflow):
    def __init__(self, summary_type="summarize_text", ai_service=None):
        self.prompt_key = summary_type
        super().__init__(ai_service)

    def parse_result(self, ai_result: str):
        """
        解析AI返回的summary文本，提取Summary、Highlights、Key Insights为结构化JSON。
        """
        self.logger.debug(f"AI原始返回: {ai_result}")
        result = {"summary": f"{ai_result}"}
        
        return result 