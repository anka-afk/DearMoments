"""
向量计算模块
"""

from dear_moments.app_context import AppContext
from dear_moments.service import Services
import numpy as np


class EmbeddingCalculator:
    """
    向量计算器, 接收到整理后的消息字符串, 建立索引的同时计算向量
    """

    def __init__(self):
        self.logger = AppContext.get_instance().get("logger")

    async def calculate_embedding(self, message: str) -> np.ndarray:
        """
        计算一段消息的嵌入向量

        Args:
            message (str): 消息内容

        Returns:
            np.ndarray: 嵌入向量
        """
        return Services.embedding_service().get_embedding(message)
