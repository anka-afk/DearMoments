from dear_moments.service import Services
from dear_moments import DearMomentsConfig
from dear_moments.core.pipeline import StoragePipeline, QueryPipeline
import asyncio
import signal


class DearMoments:
    def __init__(self):
        self.running = False
        self.stop_event = asyncio.Event()

    async def initialize(self):
        """初始化服务"""
        # 数据初始化
        # 初始化服务
        self.services = Services.get_instance()
        # 初始化配置
        self.config = DearMomentsConfig.get_instance()

        # 初始化管道处理器
        # 存储方向
        self.storage_pipeline = StoragePipeline()
        await self.storage_pipeline.create_message_processor_stage(workers=1)
        await self.storage_pipeline.create_embedding_stage(workers=1)
        await self.storage_pipeline.create_storage_stage(workers=1)
        await self.storage_pipeline.start()

        # 查询方向
        self.query_pipeline = QueryPipeline()
        await self.query_pipeline.create_query_embedding_stage(workers=1)
        await self.query_pipeline.create_vector_search_stage(workers=1)
        await self.query_pipeline.create_result_processing_stage(workers=1)
        await self.query_pipeline.start()

        self.running = True
        return self

    async def run_forever(self):
        """让服务持续运行直到收到停止信号"""
        if not self.running:
            await self.initialize()

        print("DearMoments服务已启动，等待任务...")
        await self.stop_event.wait()

    async def shutdown(self):
        """关闭服务和清理资源"""
        self.running = False
        self.stop_event.set()

        # 关闭管道
        if hasattr(self, "storage_pipeline"):
            await self.storage_pipeline.stop()
        if hasattr(self, "query_pipeline"):
            await self.query_pipeline.stop()

        # 关闭服务
        if hasattr(self, "services"):
            await self.services.close()

        print("DearMoments服务已关闭")

    # 对外提供的API方法
    async def store_message(self, message):
        """存储消息的API

        Args:
            message (str): 要存储的消息内容
        """
        if not self.running:
            raise RuntimeError("DearMoments服务尚未初始化")
        return await self.storage_pipeline.process(message)

    async def query(self, query_text):
        """查询消息的API

        Args:
            query_text (str): 要查询的文本内容
        """
        if not self.running:
            raise RuntimeError("DearMoments服务尚未初始化")
        return await self.query_pipeline.process(query_text)


if __name__ == "__main__":
    import asyncio
    import platform
    import signal

    async def main():
        dear_moments = await DearMoments().initialize()
        # 测试放入一个消息
        await dear_moments.store_message("测试消息")

        # 信号处理器
        loop = asyncio.get_event_loop()
        if platform.system() != "Windows":
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(
                    sig, lambda: asyncio.create_task(dear_moments.shutdown())
                )

        try:
            print("DearMoments服务已启动，按Ctrl+C停止服务...")
            while not dear_moments.stop_event.is_set():
                try:
                    await asyncio.wait_for(dear_moments.stop_event.wait(), 0.5)
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
        except KeyboardInterrupt:
            print("\n检测到键盘中断，正在关闭服务...")
        finally:
            if dear_moments.running:
                await dear_moments.shutdown()

    asyncio.run(main())
