# 所有Message类的基类

from datetime import datetime


class BaseMessage:
    id: str  # 消息的唯一标识符
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 消息的时间戳
    source: str  # 消息的来源
    conversation_id: str  # 消息所在对话的唯一标识符
    metadata: dict  # 消息的元数据
