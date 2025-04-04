from .base_message import BaseMessage
from dataclasses import dataclass


@dataclass
class InputMessage(BaseMessage):
    content: str  # 消息内容
    sender: str  # 消息发送者
    processed: bool = False  # 消息是否已处理
