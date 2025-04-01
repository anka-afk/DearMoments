from .embedding_service import EmbeddingService
from .network.gemini_embedding import GeminiEmbeddingService


class EmbeddingServiceFactory:
    """
    嵌入服务工厂，负责创建不同类型的嵌入服务实例
    """

    @staticmethod
    def create(service_type: str, **kwargs) -> EmbeddingService:
        """
        创建嵌入服务实例

        Args:
            service_type (str): 服务类型，如 'gemini', 'local-st'
            **kwargs: 服务特定的参数

        Returns:
            EmbeddingService: 嵌入服务实例
        """
        if service_type == "gemini":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("使用Gemini嵌入服务需要提供api_key")
            model = kwargs.get("model", "gemini-embedding-exp-03-07")
            timeout = kwargs.get("timeout", 30)
            return GeminiEmbeddingService(api_key, model, timeout)

        # elif service_type == "local-st":
        #     model_name = kwargs.get("model_name", "all-MiniLM-L6-v2")
        #     return SentenceTransformersEmbedding(model_name)

        else:
            raise ValueError(f"不支持的嵌入服务类型: {service_type}")
