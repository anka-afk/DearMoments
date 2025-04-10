import numpy as np


class Memory:
    """
    一个记忆节点, 它可以嵌套在其他记忆节点中, 形成树形结构
    """

    # 同一个深度的记忆节点的中心向量, 它代表了整个层级的父节点
    center_vector: np.ndarray
    # 记忆节点的深度, 0表示根节点, 1表示第一层子节点, 2表示第二层子节点, 以此类推
    depth: int
    # 记忆节点的向量表示
    vector: np.ndarray
    # 记忆节点的内容
    content: str
    # 记忆节点的子节点
    children: list["Memory"]
    # 记忆节点的父节点
    parent: "Memory" = None
