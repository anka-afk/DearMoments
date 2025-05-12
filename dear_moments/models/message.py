from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np
import time


@dataclass
class BaseMessage:
    # 消息id, 唯一标识
    id: str
    # 记忆id, 用于标识存储到哪个记忆库
    memory_id: str
    # 时间戳, 记录消息进入时间, 默认为当前时间
    timestamp: str = field(default_factory=lambda: str(int(time.time())), init=False)


@dataclass
class Message(BaseMessage):
    # 消息的文本内容
    content: str
    # 发送者
    sender: str
    # 携带的上下文
    context: "Context"
    # 处理状态跟踪器
    processing_state: Dict[str, Any] = field(default_factory=dict)

    def to_str(self) -> str:
        """
        将消息转换为字符串, 格式: [TIME] NAME: MESSAGE
        """
        message_strings = []
        for msg in self.context:
            time_int = int(msg.timestamp)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_int))
            message_strings.append(f"[{time_str}] {msg.sender}: {msg.content}")
        return "\n".join(message_strings)

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
            time_int = int(msg.timestamp)
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_int))
            message_strings.append(f"[{time_str}] {msg.sender}: {msg.content}")
        return "\n".join(message_strings)


@dataclass
class ContextList:
    """
    单例模式, 上下文的列表, 存储活跃的所有上下文
    """

    _instance = None
    _initialized = False

    contexts: List[Context] = None

    # 一个存储memory_id和对应context的字典, 用于查找
    memory_id_to_context: dict = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextList, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if ContextList._initialized:
            return

        # 初始化上下文列表
        self.contexts = []
        self.memory_id_to_context = {}

        ContextList._initialized = True

    @classmethod
    def get_instance(cls) -> "ContextList":
        """
        获取上下文实例

        Returns:
            ContextList: 上下文列表实例
        """
        if cls._instance is None:
            cls._instance = ContextList()
        return cls._instance

    @classmethod
    def get_by_memory_id(cls, memory_id: str) -> Context:
        """
        根据memory_id获取上下文

        Args:
            memory_id (str): 记忆ID

        Returns:
            Context: 上下文对象
        """
        instance = cls.get_instance()
        return instance.memory_id_to_context.get(memory_id, None)

    @classmethod
    def add(cls, context: Context):
        """
        添加上下文到列表

        Args:
            context (Context): 上下文对象
        """
        instance = cls.get_instance()
        instance.contexts.append(context)
        instance.memory_id_to_context[context.memory_id] = context
