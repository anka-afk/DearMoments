# 消息对象
from .base_message import BaseMessage


class Message(BaseMessage):
    def __init__(self, content, role, timestamp=None, metadata=None):
        self.content = content  # 消息内容
        self.role = role
        self.metadata = metadata if metadata is not None else {}
