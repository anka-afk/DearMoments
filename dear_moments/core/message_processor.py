# 消息预处理模块
from dear_moments.models import Message

class MessageProcessor:
    def __init__(self, llm_service, window_size=10, overlap=2):
        self.llm_service = llm_service
        self.window_size = window_size
        self.overlap = overlap
        self.buffer = []
    
    def add_message(self, message: Message):
        """添加消息到处理缓冲区

        Args:
            message (Message): 消息对象
        """
        self.buffer.append({
            "content": message.content,
        })