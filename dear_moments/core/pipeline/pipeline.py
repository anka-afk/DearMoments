import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar
from .pipeline_stage import PipelineStage


class Pipeline:
    """流水线管理器，协调多个处理阶段"""

    def __init__(self):
        self.stages: List[PipelineStage] = []
        self.logger = logging.getLogger("pipeline")

    def add_stage(self, stage: PipelineStage) -> "Pipeline":
        """添加处理阶段到流水线"""
        if self.stages:
            self.stages[-1].output_queue = stage.input_queue
        self.stages.append(stage)
        return self

    async def start(self):
        """启动所有处理阶段"""
        self.logger.info("Starting pipeline")
        for stage in self.stages:
            await stage.start()

    async def stop(self):
        """停止所有处理阶段"""
        self.logger.info("Stopping pipeline")
        for stage in reversed(self.stages):
            await stage.stop()

    async def process(self, item: Any):
        """将项目放入流水线的第一个阶段"""
        if not self.stages:
            raise ValueError("Pipeline has no stages")
        await self.stages[0].input_queue.put(item)

    async def join(self):
        """等待所有队列处理完成"""
        for stage in self.stages:
            await stage.input_queue.join()
