from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SystemPrompt:
    """
    系统提示词类, 维护一个字典, 记录每个memory_id绑定的系统提示词
    """

    system_prompts: Dict[str, str] = field(default_factory=dict)

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
