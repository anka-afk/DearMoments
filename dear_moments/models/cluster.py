# 聚类数据结构

class Cluster:
    def __init__(self, cluster_id):
        self.id = cluster_id
        self.summaries = [] # 包含的摘要
        self.label = None # 聚类标签
        self.centroid = None # 聚类中心向量