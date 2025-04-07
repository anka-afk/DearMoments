# 获得文本嵌入服务的抽象基类, 定义了文本嵌入服务的基本接口

from abc import ABC, abstractmethod
import numpy as np


class EmbeddingService(ABC):
    """
    文本嵌入服务的抽象基类
    """

    def __init__(self):
        """
        初始化文本嵌入服务
        """
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> np.ndarray:
        """
        获取文本的嵌入向量

        Args:
            text (str): 输入文本

        Returns:
            np.ndarray: 嵌入向量
        """
        pass

    def close(self):
        """
        关闭嵌入服务，释放资源
        """
        pass
