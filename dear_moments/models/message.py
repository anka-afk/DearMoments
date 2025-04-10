from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np
import time
from dear_moments.models import Context


@dataclass
class BaseMessage:
    # 消息id, 唯一标识
    id: str
    # 时间戳, 记录消息进入时间, 默认为当前时间
    timestamp: str = field(default_factory=lambda: str(int(time.time())))
    # 记忆id, 用于标识存储到哪个记忆库
    memory_id: str


@dataclass
class Message(BaseMessage):
    # 消息的文本内容
    content: str
    # 发送者
    sender: str
    # 携带的上下文
    context: Context
    # 处理状态跟踪器
    processing_state: Dict[str, Any] = field(default_factory=dict)

    def to_str(self) -> str:
        """
        将消息转换为字符串, 格式: [TIME] NAME: MESSAGE
        """
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        message_string = f"[{time_str}] {self.sender}: {self.content}"
        return message_string

    def is_processed_by(self, stage_name: str) -> bool:
        """
        检查是否被某个阶段处理过

        Args:
            stage_name (str): 阶段名称

        Returns:
            bool: 是否处理过
        """
        return stage_name in self.processing_state

    def set_embedding(self, embedding: np.ndarray):
        """
        设置嵌入向量

        Args:
            embedding (np.ndarray): 嵌入向量
        """
        self.processing_state["embedding"] = embedding

    def set_analysis_result(self, entities: List, sentiment: float) -> None:
        """
        设置分析结果

        Args:
            entities (List): _description_
            sentiment (float): _description_
        """

    def get_embedding(self) -> Optional[np.ndarray]:
        """
        获取嵌入向量

        Returns:
            Optional[np.ndarray]: 嵌入向量
        """
        return self.processing_state.get("embedding")
