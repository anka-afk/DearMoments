# 记忆管理器


class Memorymanager:
    def __init__(
        self,
        max_memories=1000,
        importance_llm=None,
        recency_weight=0.5,
        importance_weight=0.3,
        frequency_weight=0.2,
    ):
        self.max_memories = max_memories
        self.importance_llm = importance_llm
        self.memory_scores = {}  # 内存索引 -> 分数
        self.access_count = {}  # 内存索引就 -> 访问次数
        self.last_access = {}  # 内存索引 -> 上次访问时间
