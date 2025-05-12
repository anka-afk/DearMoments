import asyncio
import traceback
from typing import Any, Callable, Dict, List, Optional, TypeVar
from dear_moments.app_context import AppContext

T = TypeVar("T")
U = TypeVar("U")


class PipelineStage:
    """表示流水线中的一个处理阶段"""

    def __init__(
        self,
        name: str,
        process_func: Callable[[T], U],
        max_queue_size: int = 100,
        workers: int = 1,
    ):
        """
        初始化处理阶段

        Args:
            name: 阶段名称
            process_func: 处理函数
            max_queue_size: 队列最大容量
            workers: 并行工作者数量
        """
        self.name = name
        self.process_func = process_func
        self.input_queue = asyncio.Queue(maxsize=max_queue_size)
        self.output_queue = None  # 将在pipeline中设置
        self.workers = workers
        self.worker_tasks = []
        self.logger = AppContext.get_instance().get("logger")
        self.processed_items = 0
        self.failed_items = 0

    async def worker(self):
        """阶段工作者，不断从输入队列获取数据并处理"""
        self.logger.info(f"启动阶段 {self.name}")
        while True:
            try:
                item = await self.input_queue.get()
                if item is None:  # 结束信号
                    self.logger.info(f"工作阶段 {self.name} 收到停止信号")
                    self.input_queue.task_done()
                    break

                self.logger.debug(f"处理阶段 {self.name}")
                try:
                    result = await self.process_func(item)
                    self.processed_items += 1
                    if result is not None and self.output_queue is not None:
                        await self.output_queue.put(result)
                except Exception as e:
                    self.failed_items += 1
                    error_msg = f"在处理阶段遇到错误 {self.name}: {str(e)}"
                    stack_trace = traceback.format_exc()
                    self.logger.error(f"{error_msg}\n{stack_trace}")
                finally:
                    self.input_queue.task_done()
            except asyncio.CancelledError:
                self.logger.info(f"工作阶段 {self.name} 被取消")
                break
            except Exception as e:
                self.logger.error(f"在处理阶段遇到错误 {self.name}: {e}")

    async def start(self):
        """启动所有工作者"""
        self.worker_tasks = [
            asyncio.create_task(self.worker()) for _ in range(self.workers)
        ]

    async def stop(self):
        """停止所有工作者"""
        for _ in range(self.workers):
            await self.input_queue.put(None)

        for task in self.worker_tasks:
            await task
