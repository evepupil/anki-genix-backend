from openai import OpenAI
import os
import base64
import requests
import json
from .ai_base import AIServiceBase
from utils.logger import get_logger

class DeepseekAIService(AIServiceBase):
    def __init__(self, base_url=None, api_key=None, agent_id=None, hy_source=None, hy_user=None):
        base_url =  "http://39.104.17.54:7999/v1/"
        api_key = "8tE8bq6InCxff5mUqQZfc9aGHP6NPD80Cr/k258SiLJ9CYW8HiMzU5pREYyvnbvjBR5d0PcbgJbKaqG0NeWa+/0BBbxn5K4LxCS0jIqDD+5dtEYKFPVs3JKbP7ufu6eanr6o58XiE594CMGQut+ONmjy+36PKNAS0jvljVPrsiOQJtn6UpU8FD2I90cikHwMcbIXqw3reDfvXbdENDHN8EzTCUYjLOs98j/zloCtp1273EHn3+g/SY5LgbG2KF4n0Xb2qrGIIq6jxTO+GhoVGnu+WTNSvhnYskB6iubS7uXmD57SMATgs5VtM8WIk/2pGiobxTUpBKjq847kfG6SXQTvRBHve+NJTa0ipSBJ6c5I0bJiqnEP6XGwhnjm4h+OTR2p/muzV9OnmoPDtfP71n5H29vbxab1yWLeHFrfpWgwXK1g+VycUm0rtqj0/nabZe15kjdGSrEYFAgaX70ZWpPcgBmlXkRculXppaUvLzdLgucNqKkumLoyGdEOjqwAg6+qwfcoEt1HlMjTimI4lUMH4ggat7C2L1EsZkhb2/RuiUa7K1Xvh/8rhfFm+vq2wsos/5Tvji7kxhfdJBCThQAbb+H4QpHNuUON9r8TfKiqJXtgpvnXTvYbyAgyZXB2Myaky1Kgdfjo8B9QlfuXUg=="
        agent_id = "naQivTmsDa"
        hy_user = "d76efed3f1fb4cf1b1a3b4789111bc6c"
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
                    line = (json.loads(chunk.choices[0].delta.content).get("msg", "") or "")
                    response_text += line
            self.logger.debug(f"API调用成功: 响应长度={len(response_text)}")
            return response_text
        except Exception as e:
            self.logger.error(f"API调用失败: {str(e)}")
            raise

    def upload_files(self, files: list) -> list:
        """
        上传文件到AI服务器

        Args:
            files: 文件路径列表

        Returns:
            list: 上传成功的文件信息列表（multimedia格式）
        """
        self.logger.debug(f"upload_files调用开始: files={files}")

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
            "bat": "text", "c": "code", "cpp": "code", "cs": "code", "css": "code", "go": "code",
            "h": "code", "hpp": "code", "ini": "text", "java": "code", "js": "code", "json": "json",
            "lua": "code", "md": "text", "php": "code", "pl": "code", "py": "code", "rb": "code",
            "sh": "code", "sql": "code", "swift": "code", "tex": "text", "toml": "text", "vue": "code",
            "yaml": "yaml", "yml": "yaml", "xml": "xml", "html": "html"
        }

        for file_path in files:
            file_name = os.path.basename(file_path)
            ext = file_name.lower().split('.')[-1]

            if ext not in ext_type_map:
                self.logger.error(f"不支持的文件类型: .{ext}, 文件: {file_name}")
                raise ValueError(f"Unsupported file type: .{ext}. File: {file_name}")

            file_type = ext_type_map[ext]

            # 读取文件并编码为base64
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode("utf-8")

            # 构建上传数据
            data = {
                "agent_id": self.agent_id,
                "hy_source": self.hy_source,
                "hy_user": self.hy_user,
                "file": {
                    "file_name": file_name,
                    "file_data": file_data,
                    "file_type": 'doc',  # 统一使用doc类型
                },
            }

            # 上传文件
            resp = requests.post(url, json=data, headers=headers)

            if resp.status_code == 200:
                self.logger.info(f"文件上传成功: {file_name}")
                multimedia.append(resp.json())
            else:
                self.logger.error(f"文件上传失败: {file_name}, status={resp.status_code}, msg={resp.text}")
                raise Exception(f"文件上传失败: {file_name}, status={resp.status_code}")

        self.logger.info(f"所有文件上传完成，共 {len(multimedia)} 个文件")
        return multimedia

    def chat_with_multimedia(self, prompt: str, multimedia: list, chat_id: str = None, stream: bool = False) -> str:
        """
        使用已上传的文件进行对话

        Args:
            prompt: 对话提示词
            multimedia: 已上传的文件信息列表（由 upload_files 返回）
            chat_id: 会话ID（可选）
            stream: 是否使用流式响应

        Returns:
            str: AI响应内容
        """
        self.logger.debug(f"chat_with_multimedia调用开始: prompt长度={len(prompt)}, multimedia数量={len(multimedia)}")

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

            # 拼接流式响应
            response_text = ""
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    line = (json.loads(chunk.choices[0].delta.content).get("msg", "") or "")
                    response_text += line

            self.logger.debug(f"chat_with_multimedia响应成功: 响应长度={len(response_text)}")
            return response_text

        except Exception as e:
            self.logger.error(f"chat_with_multimedia API调用失败: {str(e)}")
            raise

    def chat_with_files(self, prompt: str, files: list, stream: bool = False) -> str:
        """
        支持文件上传的chat，files为文件路径列表。支持图片、office文档、pdf、文本、代码等类型。

        这是一个便捷方法，内部调用 upload_files 和 chat_with_multimedia

        Args:
            prompt: 对话提示词
            files: 文件路径列表
            stream: 是否使用流式响应

        Returns:
            str: AI响应内容
        """
        self.logger.debug(f"chat_with_files调用开始: prompt长度={len(prompt)}, files={files}")

        # 1. 上传文件
        multimedia = self.upload_files(files)

        # 2. 使用上传的文件进行对话
        response_text = self.chat_with_multimedia(prompt, multimedia, chat_id=None, stream=stream)

        return response_text

    