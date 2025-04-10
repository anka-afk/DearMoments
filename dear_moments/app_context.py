from typing import Dict, Any
import logging
import json


class AppContext:
    """
    应用上下文，管理全局共享对象
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppContext, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if AppContext._initialized:
            return

        self._shared_objects: Dict[str, Any] = {}
        self._init_shared_objects()

        AppContext._initialized = True

    def _init_shared_objects(self) -> None:
        """初始化共享对象"""
        # 初始化全局logger
        logger = logging.getLogger("DearMoments")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # 从配置中获取日志级别
        from dear_moments.config import DearMomentsConfig

        config = DearMomentsConfig.get_instance()
        log_level = config.get("app.log_level", "INFO")
        logger.setLevel(getattr(logging, log_level))

        # 注册共享logger
        self.register("logger", logger)

        # 初始化prompt资源

    def set_logger(self, logger: logging.Logger) -> None:
        """
        设置logger, 用于外部传入logger

        Args:
            logger (logging.Logger): logger实例
        """
        for handler in self._shared_objects["logger"].handlers:
            self._shared_objects["logger"].removeHandler(handler)
        self._shared_objects["logger"] = logger

    def register(self, name: str, obj: Any) -> None:
        """注册共享对象"""
        self._shared_objects[name] = obj

    def get(self, name: str) -> Any:
        """获取共享对象"""
        if name not in self._shared_objects:
            raise KeyError(f"共享对象 {name} 未注册")
        return self._shared_objects[name]

    @classmethod
    def get_instance(cls) -> "AppContext":
        """获取上下文实例"""
        if cls._instance is None:
            cls._instance = AppContext()
        return cls._instance

    @classmethod
    def shared(cls, name: str) -> Any:
        """通过类名直接访问共享对象"""
        return cls.get_instance().get(name)

    @classmethod
    def logger(cls) -> logging.Logger:
        """获取全局logger"""
        return cls.shared("logger")
