from typing import Dict, Any, Optional


class DearMomentsConfig:
    """
    配置类, 用于存储整个程序共享的配置
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DearMomentsConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if DearMomentsConfig._initialized:
            return

        # 加载本地默认配置, 暂定目录为config.json
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                import json

                self._config = json.load(f)
        except FileNotFoundError:
            self._config = {
                "services": {
                    "llm": {
                        "type": "gemini",
                        "api_key": "",
                        "model": "gemini-2.0-flash",
                        "timeout": 30,
                    },
                    "embedding": {
                        "type": "gemini",
                        "api_key": "",
                        "model": "gemini-embedding-exp-03-07",
                        "timeout": 30,
                    },
                },
                "app": {
                    "language": "zh-CN",
                    "log_level": "INFO",
                    "max_queue_size": 100,
                    "workers": 2,
                },
            }
        DearMomentsConfig._initialized = True

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        获取配置值

        Args:
            key (str): 配置项的键
            default (Optional[Any], optional): 如果未找到配置项时的默认值. Defaults to None.

        Returns:
            Any: 配置项的值
        """
        keys = key.split(".")
        config = self._config

        for k in keys:
            if k not in config:
                return default
            config = config[k]
        return config

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key (str): 配置项的键
            value (Any): 配置项的值
        """
        keys = key.split(".")
        config = self._config

        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @classmethod
    def get_instance(cls) -> "DearMomentsConfig":
        """获取配置实例"""
        if cls._instance is None:
            cls._instance = DearMomentsConfig()
        return cls._instance
