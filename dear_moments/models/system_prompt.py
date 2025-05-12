from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SystemPrompt:
    """
    系统提示词类, 维护一个字典, 记录每个memory_id绑定的系统提示词
    单例模式实现
    """

    _instance = None
    _initialized = False

    system_prompts: Dict[str, str] = field(default_factory=dict)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemPrompt, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if SystemPrompt._initialized:
            return

        # 初始化系统提示词字典
        self.system_prompts = {}
        SystemPrompt._initialized = True

    @classmethod
    def get_instance(cls) -> "SystemPrompt":
        """
        获取系统提示词实例

        Returns:
            SystemPrompt: 系统提示词实例
        """
        if cls._instance is None:
            cls._instance = SystemPrompt()
        return cls._instance

    def get(self, memory_id: str) -> str:
        """
        获取系统提示词

        Args:
            memory_id (str): 记忆id

        Returns:
            str: 系统提示词
        """
        return self.system_prompts.get(memory_id, "")

    def set(self, memory_id: str, system_prompt: str) -> None:
        """
        设置系统提示词

        Args:
            memory_id (str): 记忆id
            system_prompt (str): 系统提示词
        """
        self.system_prompts[memory_id] = system_prompt
