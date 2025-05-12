from typing import Any, Callable, Dict, List, Optional, Type
from .base_pipeline import BasePipeline
from .pipeline_stage import PipelineStage


class StoragePipeline(BasePipeline):
    """存储管道，用于处理和存储消息"""

    def __init__(self):
        super().__init__("存储管道")

    async def create_message_processor_stage(
        self, max_queue_size: int = 100, workers: int = 2
    ):
        """创建消息处理阶段"""
        from dear_moments.core.storage_processors.message_processor import (
            MessageProcessor,
        )

        async def process_message(message: Any):
            processor = MessageProcessor()
            await processor.save_to_context(message)
            event_frame = await processor.message_to_event_frame(message)
            return event_frame

        stage = PipelineStage("消息处理", process_message, max_queue_size, workers)
        self.add_stage(stage)
        return self

    async def create_embedding_stage(self, max_queue_size: int = 100, workers: int = 2):
        """创建嵌入计算阶段"""
        from dear_moments.service import Services
        import json

        async def calculate_embedding(event_frame: Any):
            if not event_frame:
                return None

            embedding_service = Services.embedding_service()
            embedding = await embedding_service.get_embedding_async(
                json.dumps(event_frame)
            )
            return {"event_frame": event_frame, "embedding": embedding}

        stage = PipelineStage("嵌入计算", calculate_embedding, max_queue_size, workers)
        self.add_stage(stage)
        return self

    async def create_storage_stage(self, max_queue_size: int = 100, workers: int = 1):
        """创建向量存储阶段"""
        from dear_moments.service import Services

        async def store_vector(data: Any):
            if not data:
                return None

            event_frame = data["event_frame"]
            embedding = data["embedding"]

            storage_service = Services.vector_storage()
            result = await storage_service.store(
                event_frame, embedding, metadata={"type": event_frame["type"]}
            )
            return result

        stage = PipelineStage("向量存储", store_vector, max_queue_size, workers)
        self.add_stage(stage)
        return self
