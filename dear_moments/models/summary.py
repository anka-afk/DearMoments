# 摘要类型

class Summary:
    def __init__(self, text, source_messages, timestamp_range, vector=None):
        self.text = text # 摘要文本
        self.source_messages = source_messages # 原始消息
        self.timestamp_range = timestamp_range # (开始时间, 结束时间)
        self.vector = vector # 向量表示
        self.cluster_id = None # 聚类ID
        self.label = None # 标签