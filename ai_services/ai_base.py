from abc import ABC, abstractmethod

class AIServiceBase(ABC):
    @abstractmethod
    def chat(self, prompt: str, stream: bool = False) -> str:
        """
        通用AI对话接口，返回AI回复内容。
        """
        pass 