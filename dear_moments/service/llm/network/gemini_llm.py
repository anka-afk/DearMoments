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

    async def get_response(self, prompt):
        pass
