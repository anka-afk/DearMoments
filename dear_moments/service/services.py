from dear_moments.service.embedding import EmbeddingService, EmbeddingServiceFactory
from dear_moments.service.llm import LLMService, LLMServiceFactory
from typing import Dict, Type, TypeVar, Any

T = TypeVar("T")


class Services:
    """
    单例模式
    所有服务的集合
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Services, cls).__new__(cls)
        return cls._instance

    def __init__(
        self, embedding_service_type: str = "gemini", llm_service_type: str = "gemini"
    ):
        if Services._initialized:
            return
        self._services: Dict[str, Any] = {}

        self._init_all_services(embedding_service_type, llm_service_type)

        Services._initialized = True

    def _init_all_services(
        self, embedding_service_type: str, llm_service_type: str
    ) -> None:
        """初始化所有服务"""
        # 初始化嵌入服务
        self.register_service(
            EmbeddingService, EmbeddingServiceFactory.create(embedding_service_type)
        )

        # 初始化LLM服务
        self.register_service(LLMService, LLMServiceFactory.create(llm_service_type))

    @classmethod
    def get_instance(cls) -> "Services":
        """获取Services单例实例"""
        if cls._instance is None:
            cls._instance = Services()
        return cls._instance

    def register_service(self, service_type: Type[T], instance: T) -> None:
        """注册服务实例"""
        self._services[service_type.__name__] = instance

    def get_service(self, service_type: Type[T]) -> T:
        """获取指定类型的服务实例"""
        service_name = service_type.__name__
        if service_name not in self._services:
            raise KeyError(f"服务 {service_name} 未注册")
        return self._services[service_name]

    def get_embedding_service(self) -> EmbeddingService:
        """获取嵌入服务"""
        return self.get_service(EmbeddingService)

    def get_llm_service(self) -> LLMService:
        """获取LLM服务"""
        return self.get_service(LLMService)

    @classmethod
    def embedding_service(cls) -> EmbeddingService:
        """通过类名直接访问嵌入服务"""
        return cls.get_instance().get_embedding_service()

    @classmethod
    def llm_service(cls) -> LLMService:
        """通过类名直接访问LLM服务"""
        return cls.get_instance().get_llm_service()

    @classmethod
    def service(cls, service_type: Type[T]) -> T:
        """通过类名直接访问指定类型的服务"""
        return cls.get_instance().get_service(service_type)
