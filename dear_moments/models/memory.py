from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np
import time
from uuid import uuid4


@dataclass
class Memory:
    # 记忆唯一标识
    id: str = field(default_factory=lambda: str(uuid4()))
    # 创建时间戳
    created_at: float = field(default_factory=time.time)
    # 最后访问时间戳
    last_accessed_at: float = field(default_factory=time.time)
    # 记忆内容
    content: str
    # 内容嵌入向量
    embedding: np.ndarray
    # 重要性分数(0-1)
    importance: float = 0.5
    # 访问计数
    access_count: int = 0
    # 关联标签
    tags: List[str] = field(default_factory=list)
    # 关联实体(例如：人物、地点、事件等)
    entities: Dict[str, Any] = field(default_factory=dict)
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    # 原始消息ID列表(可关联到原始消息)
    source_message_ids: List[str] = field(default_factory=list)

    def update_access(self):
        """更新访问信息"""
        self.last_accessed_at = time.time()
        self.access_count += 1

    def calculate_retrieval_score(self, current_time: float = None) -> float:
        """计算检索分数(结合重要性、时间衰减和访问频率)"""
        if current_time is None:
            current_time = time.time()

        # 时间衰减因子(近期记忆得分更高)
        time_factor = 1.0 / (
            1.0 + 0.1 * (current_time - self.created_at) / 86400
        )  # 86400秒=1天

        # 访问频率因子(常访问的记忆得分更高)
        access_factor = min(1.0, 0.1 * self.access_count)

        # 综合得分
        return self.importance * 0.6 + time_factor * 0.3 + access_factor * 0.1
