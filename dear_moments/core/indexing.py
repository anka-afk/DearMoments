# 索引服务
from dear_moments.models import Summary


class MemoryIndex:
    def __init__(self, vector_dimension: int):
        """
        记忆索引服务

        Args:
            vector_dimension (int): 向量维度
        """
        self.keyword_index = {}  # 关键词 -> [摘要索引]
        self.vector_index = self._init_vector_index(vector_dimension)
        self.summary_store = []  # 存储所有摘要

    def _init_vector_index(self, dimension: int):
        """初始化向量索引

        Args:
            dimension (int): 向量维度
        """
        try:
            import faiss

            return faiss.IndexFlatIP(dimension)  # 使用内积作为相似度度量
        except ImportError:
            raise ImportError("请安装faiss库以使用向量索引功能: pip install faiss-cpu")

    def add_summary(self, embedded_summary: Summary, label_data=None):
        """添加摘要到索引

        Args:
            embedded_summary (Summary): 嵌入的摘要对象
            label_data (optional): 标签数据. Defaults to None.
        """
        # 添加到向量索引
        import numpy as np

        vector = np.array([embedded_summary.vector], dtype=np.float32)
        index = len(self.summary_store)
        self.vector_index.add(vector)

        # 添加到摘要存储
        self.summary_store.append(embedded_summary)

        # 如果有标签, 添加到关键词索引
        if label_data:
            # 添加标签
            self._add_to_key_word_index(label_data["label"], index)
            # 添加关键词
            for keyword in label_data["keywords"]:
                self._add_to_key_word_index(keyword, index)
        return index

    def _add_to_keyword_index(self, keyword, index):
        """添加关键词到索引

        Args:
            keyword (str): 关键词
            index (int): 索引位置
        """
        keyword = keyword.lower()
        if keyword not in self.keyword_index:
            self.keyword_index[keyword] = []
        self.keyword_index[keyword].append(index)

    def search_by_vector(self, query_vector, top_k=5):
        """通过向量搜索相似摘要

        Args:
            query_vector (np.ndarray): 查询向量
            top_k (int, optional): 返回的相似摘要数量. Defaults to 5.
        """
        import numpy as np

        query_vector = np.array([query_vector], dtype=np.float32)
        distances, indices = self.vector_index.search(query_vector, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.summary_store):
                summary = self.summary_store[idx]
                results.append({"summary": summary, "score": float(distances[0][i])})
        return results

    def search_by_keyword(self, keywords, top_k=5):
        """通过关键词搜索相似摘要"""
        results = {}  # 索引 -> 匹配次数
        for keyword in keywords:
            keyword - keyword.lower()
            if keyword in self.keyword_index:
                for index in self.keyword_index[keyword]:
                    if index not in results:
                        results[index] = 0
                    results[index] += 1
        # 排序
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        return [
            {"summary": self.summary_store[idx], "score": count}
            for idx, count in sorted_results
        ]
