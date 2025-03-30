# 向量嵌入模块
from dear_moments.models import Summary


class EmbeddingService:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def embed_summary(self, summary: Summary):
        """将摘要转换为向量表示"""
        # 提取摘要文本
        text = summary.text

        # 生成向量
        vector = self.embedding_model.encode(text)

        # 将向量存储在摘要对象中
        summary.vector = vector

        # 返回有向量的增强摘要
        return summary
