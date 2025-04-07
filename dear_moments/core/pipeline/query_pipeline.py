from typing import Any, Callable, Dict, List, Optional, Type
from .base_pipeline import BasePipeline
from .pipeline_stage import PipelineStage


class QueryPipeline(BasePipeline):
    """查询管道，用于处理查询请求"""

    def __init__(self):
        super().__init__("查询管道")

    async def create_query_embedding_stage(
        self, max_queue_size: int = 100, workers: int = 2
    ):
        """创建查询嵌入阶段"""
        from dear_moments.service import Services

        async def calculate_query_embedding(query: str):
            if not query:
                return None

            embedding_service = Services.embedding_service()
            embedding = await embedding_service.get_embedding_async(query)
            return {"query": query, "embedding": embedding}

        stage = PipelineStage(
            "查询嵌入", calculate_query_embedding, max_queue_size, workers
        )
        self.add_stage(stage)
        return self

    async def create_vector_search_stage(
        self, max_queue_size: int = 100, workers: int = 2
    ):
        """创建向量搜索阶段"""
        from dear_moments.service import Services

        async def search_vectors(data: Any):
            if not data:
                return None

            query = data["query"]
            embedding = data["embedding"]

            storage_service = Services.vector_storage()
            results = await storage_service.search(embedding, top_k=5)
            return {"query": query, "results": results}

        stage = PipelineStage("向量搜索", search_vectors, max_queue_size, workers)
        self.add_stage(stage)
        return self

    async def create_result_processing_stage(
        self, max_queue_size: int = 100, workers: int = 2
    ):
        """创建结果处理阶段"""
        from dear_moments.service import Services

        async def process_results(data: Any):
            if not data:
                return None

            # 对搜索结果的后处理逻辑

            return data["results"]

        stage = PipelineStage("结果处理", process_results, max_queue_size, workers)
        self.add_stage(stage)
        return self
