# 用于请求llm服务的抽象基类

from abc import ABC, abstractmethod


class LLMService(ABC):
    """
    LLM服务的抽象基类
    """

    @abstractmethod
    def __init__(self):
        """
        初始化LLM服务

        :param config: LLM服务的配置参数
        """
        pass

    @abstractmethod
    def get_response(self, prompt: str) -> str:
        """
        获取LLM服务的响应

        :param prompt: 输入的提示文本
        :return: LLM服务的响应文本
        """
        pass
