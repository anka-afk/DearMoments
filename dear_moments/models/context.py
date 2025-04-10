from dataclasses import dataclass
from typing import List
from dear_moments.models import Message


@dataclass
class Context:
    """
    上下文类, 用于存储上下文信息
    """

    memory_id: str
    context: List[Message]

    def add(self, message: Message):
        """
        加入一条消息到上下文

        Args:
            message (Message): 消息对象
        """
        self.context.append(message)

    def to_str(self) -> str:
        """
        将上下文转换为字符串, 格式: [TIME] NAME: MESSAGE

        Returns:
            str: 格式化后的上下文字符串
        """
        message_strings = []
        for msg in self.context:
            time_str = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            message_strings.append(f"[{time_str}] {msg.sender}: {msg.content}")
        return "\n".join(message_strings)
