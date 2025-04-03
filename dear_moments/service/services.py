from dear_moments.service.embedding import EmbeddingService, EmbeddingServiceFactory
from dear_moments.service.llm import LLMService


class Services:
    """
    单例模式
    所有服务的集合
    """

    embedding_service: EmbeddingService = None
    llm_service: LLMService = None
