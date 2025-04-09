# 记忆数据模型的抽象基类
from abc import ABC, abstractmethod


class Memory(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def save(self):
        pass

    @abstractmethod
    async def load(self):
        pass
