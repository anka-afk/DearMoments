# 主引擎
from dear_moments.core import Message_processor


class DearMomentsEngine:
    def __init__(self):
        # 初始化各个组件
        self.message_processor = Message_processor()