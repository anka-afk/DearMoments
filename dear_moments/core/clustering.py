# 聚类管理器
import numpy as np
from scipy.spatial.distance import cosine
from dear_moments.models import Summary


class ClusteringManager:
    def __init__(
        self, clustering_algorithm="hdbscan", min_cluster_size=5, refit_threshold=50
    ):
        self.algorithm = clustering_algorithm
        self.min_cluster_size = min_cluster_size
        self.refit_threshold = refit_threshold
        self.clusters = {}  # 字典: 聚类ID -> 聚类数据
        self.vectors = np.empty((0, 0))  # 所有向量
        self.summaries = []  # 所有摘要
        self.model = self._init_model()
        self.pending_count = 0  # 待处理的向量数量

    def _init_model(self):
        """初始化聚类模型"""
        if self.algorithm == "hdbscan":
            from hdbscan import HDBSCAN

            return HDBSCAN(min_cluster_size=self.min_cluster_size, metric="cosine")
        elif self.algorithm_type == "kmeans":
            from sklearn.cluster import MiniBatchKMeans

            return MiniBatchKMeans(
                n_clusters=max(10, len(self.vectors) // 20),
                random_state=42,
            )
        else:
            pass

    def add_summary(self, embedded_summary: Summary):
        """添加新摘要并决定是否需要重新聚类

        Args:
            embedded_summary (Summary): 带有 vector 的摘要对象
        """
        if self.vectors.size == 0:
            # 如果没有向量, 初始化向量数组
            self.vectors = np.array([embedded_summary.vector])
        else:
            self.vectors = np.vstack((self.vectors, embedded_summary.vector))
        self.pending_count += 1
        # 判断是否需要重新聚类
        if self.pending_count >= self.refit_threshold:
            self.refit_clusters()

    def refit_clusters(self):
        """重新计算所有聚类"""
        if len(self.vectors) < self.min_cluster_size:
            # 如果向量数量小于最小聚类大小, 不进行聚类
            return

        # 重新拟合模型
        self.model = self._init_model()
        labels = self.model.fit_predict(self.vectors)

        # 重新组织聚类
        self.clusters = {}
        for i, label in enumerate(labels):
            if label == -1:
                # 噪声
                continue

            if label not in self.clusters:
                self.clusters[label] = []
            self.clusters[label].append(self.vectors[i])
        self.pending_count = 0

    def _assign_to_nearest_cluster(self, embedded_summary: Summary):
        """临时将新摘要分配到最近的聚类

        Args:
            embedded_summary (Summary): 带有 vector 的摘要对象
        """
        if not self.clusters:
            # 如果没有聚类, 返回
            return

        # 找到最相似的聚类
        vector = embedded_summary.vector
        best_cluster = None
        best_similarity = -1

        for cluster_id, indices in self.clusters.items():
            cluster_vectors = [self.vectors[i] for i in indices]
            centroid = np.mean(cluster_vectors, axis=0)
            similarity = 1 - cosine(vector, centroid)

            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster = cluster_id

        # 如果相似度足够高, 将摘要分配到该聚类
        if best_similarity > 0.6 and best_cluster is not None:
            self.clusters[best_cluster].append(len(self.vectors) - 1)
