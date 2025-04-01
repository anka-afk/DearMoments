# 向量嵌入模块
from dear_moments.models import Summary
from dear_moments.service.embedding import EmbeddingService


class SummaryEmbedder:
    def __init__(self, embedding_service: EmbeddingService):
        """初始化摘要嵌入器

        Args:
            embedding_service (EmbeddingService): 嵌入服务实例
        """
        self.embedding_service = embedding_service

    def embed_summary(self, summary: Summary) -> Summary:
        """将摘要转换为向量表示

        Args:
            summary (Summary): 摘要对象

        Returns:
            Summary: 增强的摘要对象(带向量)
        """
        # 提取摘要文本
        text = summary.text

        # 生成向量
        vector = self.embedding_service.get_embedding(text)

        # 将向量存储在摘要对象中
        summary.vector = vector

        # 返回有向量的增强摘要
        return summary
