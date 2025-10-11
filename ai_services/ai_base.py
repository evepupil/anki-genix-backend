from abc import ABC, abstractmethod

class AIServiceBase(ABC):
    @abstractmethod
    def chat(self, prompt: str, stream: bool = False) -> str:
        """
        通用AI对话接口，返回AI回复内容。
        """
        pass

    def chat_with_files(self, prompt: str, files: list, stream: bool = False) -> str:
        """
        支持文件上传的AI对话接口，返回AI回复内容。
        默认实现：如果子类不支持文件上传，则忽略文件直接调用chat方法。
        """
        return self.chat(prompt, stream) 