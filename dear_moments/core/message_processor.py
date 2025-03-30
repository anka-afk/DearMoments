# 消息预处理模块
from dear_moments.models import Message, Summary


class MessageProcessor:
    def __init__(self, llm_service, window_size: int = 10, overlap: int = 2):
        self.llm_service = llm_service
        self.window_size = window_size
        self.overlap = overlap  # 重叠窗口大小, 用于保持上下文连贯性
        self.buffer = []

    def add_message(self, message: Message):
        """添加消息到处理缓冲区

        Args:
            message (Message): 消息对象
        """
        self.buffer.append(
            {
                "content": message.content,
            }
        )

    def process_window(self):
        """对当前窗口进行摘要处理"""
        messages_to_summarize = self.buffer[-self.window_size :]

        # 调用LLM进行摘要
        summary = self.llm_service.summarize(
            messages_to_summarize, prompt="请提取这段对话中的关键信息, 主题和重要细节"
        )

        # 清理缓冲区, 保留overlap用于下次摘要的连贯性
        self.buffer = self.buffer[-(self.overlap)]

        return Summary(
            text=summary,
            source_messages=messages_to_summarize,
            timestamp_range=(
                messages_to_summarize[0]["timestamp"],
                messages_to_summarize[-1]["timestamp"],
            ),
        )
