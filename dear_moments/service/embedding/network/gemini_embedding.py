import aiohttp
from ..embedding_service import EmbeddingService
import numpy as np


class GeminiEmbeddingService(EmbeddingService):
    """
    使用Gemini API的嵌入服务
    """

    def __init__(self, api_key, model="gemini-embedding-exp-03-07", timeout=30):
        """
        初始化Gemini嵌入服务

        Args:
            api_key (str): Gemini API密钥
            model (str): 嵌入模型名称
            timeout (int): 请求超时时间(秒)
        """
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={api_key}"
        self.client = None

    def _ensure_client(self):
        """确保异步HTTP客户端已创建"""
        if self.client is None:
            self.client = aiohttp.ClientSession()
        return self.client

    async def get_embedding(self, text: str) -> np.ndarray:
        """
        获取文本的嵌入向量

        Args:
            text (str): 输入文本

        Returns:
            np.ndarray: 嵌入向量
        """
        client = self._ensure_client()
        headers = {"Content-Type": "application/json"}
        data = {
            "model": f"models/{self.model}",
            "content": {"parts": [{"text": text}]},
        }

        async with client.post(
            self.base_url, headers=headers, json=data, timeout=self.timeout
        ) as response:
            if response.status == 200:
                result = await response.json()
                if "embedding" in result and "values" in result["embedding"]:
                    # 性能考虑, float32类型的numpy数组比list更快
                    return np.array(result["embedding"]["values"], dtype=np.float32)
                else:
                    raise ValueError(f"API返回格式异常: {result}")
            else:
                error_text = await response.text()
                raise Exception(f"API请求失败: {response.status} - {error_text}")

    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.close()
            self.client = None
