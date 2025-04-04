from .llm_service import LLMService
from .network.gemini_llm import GeminiLLMService


class LLMServiceFactory:
    """
    LLM服务工厂，负责创建不同类型的LLM服务实例
    """

    @staticmethod
    def create(service_type: str, **kwargs) -> LLMService:
        """
        创建LLM服务实例

        Args:
            service_type (str): LLM服务类型，如 'gemini'
            **kwargs: LLM服务特定的参数

        Returns:
            LLMService: LLM服务实例
        """
        if service_type == "gemini":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("使用Gemini LLM服务需要提供api_key")
            model = kwargs.get("model", "gemini-2.0-flash")
            timeout = kwargs.get("timeout", 30)
            return GeminiLLMService(api_key, model, timeout)

        else:
            raise ValueError(f"不支持的LLM服务类型: {service_type}")
