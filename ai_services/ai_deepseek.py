from openai import OpenAI
import os
from .ai_base import AIServiceBase
from utils.logger import get_logger

class DeepseekAIService(AIServiceBase):
    def __init__(self, base_url=None, api_key=None, agent_id=None, hy_source=None, hy_user=None):
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL")
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.agent_id = agent_id or os.getenv("DEEPSEEK_AGENT_ID")
        self.hy_source = hy_source or os.getenv("DEEPSEEK_HY_SOURCE", "web")
        self.hy_user = hy_user or os.getenv("DEEPSEEK_HY_USER")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self.logger = get_logger(name="ai_service.deepseek")
        self.logger.info(f"初始化 DeepseekAIService: base_url={self.base_url}, agent_id={self.agent_id}")

    def chat(self, prompt: str, stream: bool = False) -> str:
        self.logger.debug(f"API调用开始: prompt长度={len(prompt)}, stream={stream}")
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v3",
                messages=[{"role": "user", "content": prompt}],
                stream=stream,
                extra_body={
                    "hy_source": self.hy_source,
                    "hy_user": self.hy_user,
                    "agent_id": self.agent_id,
                    "should_remove_conversation": True,
                },
            )
            result = response.choices[0].message.content
            self.logger.debug(f"API调用成功: 响应长度={len(result)}")
            return result
        except Exception as e:
            self.logger.error(f"API调用失败: {str(e)}")
            raise