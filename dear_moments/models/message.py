# 消息对象
import time


class Message:
    def __init__(self, content, role, timestamp=None, metadata=None):
        self.content = content  # 消息内容
        self.role = role
        self.timestamp = timestamp or time.time()
        self.metadata = metadata if metadata is not None else {}
