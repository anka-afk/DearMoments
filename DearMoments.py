from dear_moments.storage_processors import MessageProcessor
from dear_moments.service import Services
from dear_moments import DearMomentsConfig


class DearMoments:
    def __init__(self):
        # 数据初始化
        # 初始化服务
        self.services = Services.get_instance()
        # 初始化配置
        self.config = DearMomentsConfig.get_instance()

        # 初始化组件
        # 初始化消息处理器
        self.message_processor = MessageProcessor()
