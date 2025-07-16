from openai import OpenAI
import os
import base64
import requests
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
                stream=True,
                extra_body={
                    "hy_source": self.hy_source,
                    "hy_user": self.hy_user,
                    "agent_id": self.agent_id,
                    "should_remove_conversation": True,
                },
            )
            # 拼接流式响应
            response_text = ""
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    line = chunk.choices[0].delta.content
                    response_text += line.replace('[text]', '')
            self.logger.debug(f"API调用成功: 响应长度={len(response_text)}")
            return response_text
        except Exception as e:
            self.logger.error(f"API调用失败: {str(e)}")
            raise

    def chat_with_files(self, prompt: str, files: list, stream: bool = False) -> str:
        """
        支持文件上传的chat，files为文件路径列表。支持图片、office文档、pdf、文本、代码等类型。
        """
        self.logger.debug(f"chat_with_files调用开始: prompt长度={len(prompt)}, files={files}")
        multimedia = []
        hy_token = self.api_key
        url = f"{self.base_url}upload"
        headers = {"Authorization": f"Bearer {hy_token}"}
        # 支持的扩展名与类型映射
        ext_type_map = {
            # 图片
            "jpg": "image", "jpeg": "image", "png": "image", "webp": "image", "bmp": "image", "gif": "image",
            # office
            "xls": "excel", "xlsx": "excel", "ppt": "ppt", "pptx": "ppt", "doc": "doc", "docx": "doc",
            # pdf
            "pdf": "pdf",
            # 文本
            "txt": "text", "csv": "csv", "text": "text",
            # 代码/配置/标记
            "bat": "text", "c": "code", "cpp": "code", "cs": "code", "css": "code", "go": "code", "h": "code", "hpp": "code", "ini": "text", "java": "code", "js": "code", "json": "json", "lua": "code", "md": "text", "php": "code", "pl": "code", "py": "code", "rb": "code", "sh": "code", "sql": "code", "swift": "code", "tex": "text", "toml": "text", "vue": "code", "yaml": "yaml", "yml": "yaml", "xml": "xml", "html": "html"
        }
        for file_path in files:
            file_name = os.path.basename(file_path)
            ext = file_name.lower().split('.')[-1]
            if ext not in ext_type_map:
                raise ValueError(f"Unsupported file type: .{ext}. File: {file_name}")
            file_type = ext_type_map[ext]
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode("utf-8")
            data = {
                "agent_id": self.agent_id,
                "hy_source": self.hy_source,
                "hy_user": self.hy_user,
                "file": {
                    "file_name": file_name,
                    "file_data": file_data,
                    "file_type": file_type,
                },
            }
            resp = requests.post(url, json=data, headers=headers)
            if resp.status_code == 200:
                self.logger.info(f"文件上传成功: {file_name}")
                multimedia.append(resp.json())
            else:
                self.logger.error(f"文件上传失败: {file_name}, status={resp.status_code}, msg={resp.text}")
        # chat
        chat_id = None  # 可根据需要传递chat_id
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v3",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                extra_body={
                    "hy_source": self.hy_source,
                    "hy_user": self.hy_user,
                    "agent_id": self.agent_id,
                    "should_remove_conversation": False,
                    "multimedia": multimedia,
                    "chat_id": chat_id,
                },
            )
            response_text = ""
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    line = chunk.choices[0].delta.content
                    response_text += line.replace('[text]', '')
            self.logger.debug(f"chat_with_files响应成功: 响应长度={len(response_text)}")
            return response_text
        except Exception as e:
            self.logger.error(f"chat_with_files API调用失败: {str(e)}")
            raise

    