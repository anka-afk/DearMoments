import aiohttp
from ..llm_service import LLMService


class GeminiLLMService(LLMService):
    """
    使用Gemini API的LLM服务
    """

    def __init__(
        self, api_key: str, model: str = "gemini-2.0-flash", timeout: int = 30
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        self.client = None

    def _ensure_client(self):
        """确保异步HTTP客户端已创建"""
        if self.client is None:
            self.client = aiohttp.ClientSession()
        return self.client

    async def get_response(self, prompt: str) -> str:
        """
        异步获取llm的回复

        Args:
            prompt (str): 输入提示文本

        Returns:
            str: LLM的回复文本
        """
        client = self._ensure_client()

        # 构建请求头
        headers = {"Content-Type": "application/json"}

        # 构建请求体
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["Text"]},
        }

        # 发送请求
        async with client.post(
            self.base_url, json=payload, headers=headers, timeout=self.timeout
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Gemini API错误: {resp.status}, {error_text}")

            try:
                response_data = await resp.json()
            except Exception as e:
                text = await resp.text()
                raise Exception(f"Gemini返回了非JSON数据: {text}")

            # 解析响应
            if "candidates" not in response_data:
                raise Exception(f"Gemini返回异常结果: {response_data}")

            candidate = response_data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                response_text = ""
                for part in parts:
                    if "text" in part:
                        response_text += part["text"]
                return response_text

            raise Exception(f"无法从Gemini响应中提取文本: {response_data}")

    def close(self):
        """关闭HTTP客户端"""
        if self.client:
            self.client.close()
            self.client = None
