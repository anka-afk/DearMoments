import asyncio
from typing import Any, Dict, List, Optional, TypeVar
from .pipeline_stage import PipelineStage
from dear_moments.app_context import AppContext


class BasePipeline:
    """
    基础管道类, 存储和查询管道的基类
    """

    def __init__(self, name: str):
        """
        初始化管道

        Args:
            name (str): 管道名称
        """
        self.name = name
        self.stages: List[PipelineStage] = []
        self.logger = AppContext.get_instance().get("logger")
        self._is_running = False

    def add_stage(self, stage: PipelineStage) -> "BasePipeline":
        """
        添加处理阶段到管道

        Args:
            stage (PipelineStage): 处理阶段

        Returns:
            BasePipeline: 管道实例
        """
        if self._is_running:
            raise RuntimeError("Cannot add stage while pipeline is running")

        if self.stages:
            self.stages[-1].output_queue = stage.input_queue
        self.stages.append(stage)
        return self

    async def start(self):
        """
        启动所有处理阶段
        """
        self.logger.info(f"Starting pipeline: {self.name}")
        for stage in self.stages:
            await stage.start()
        self._is_running = True

    async def stop(self):
        """
        停止所有处理阶段
        """
        self.logger.info(f"Stopping pipeline: {self.name}")
        for stage in reversed(self.stages):
            await stage.stop()
        self._is_running = False

    async def process(self, item: Any):
        """
        将一个东西放入管道的第一个阶段

        Args:
            item (Any): 要处理的项目
        """
        if not self.stages:
            raise ValueError(f"Pipeline{self.name} has no stages")
        if not self._is_running:
            raise RuntimeError(f"Pipeline{self.name} is not running")
        await self.stages[0].input_queue.put(item)

    async def join(self):
        """
        等待所有队列处理完成
        """
        for stage in self.stages:
            await stage.input_queue.join()

    def get_statistics(self) -> Dict[str, Dict[str, int]]:
        stats = {}
        for stage in self.stages:
            stats[stage.name] = {
                "queue_size": stage.input_queue.qsize(),
                "workers": stage.workers,
                "processed_items": stage.processed_items,
                "failed_items": stage.failed_items,
            }
        return stats
