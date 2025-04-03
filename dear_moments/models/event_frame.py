from dataclasses import dataclass


@dataclass
class EventFrame:
    """
    事件框架表示
    """

    type: str = None  # 事件类型
    participants: list[str] = None  # 参与者列表
    time: str = None  # 事件发生时间
    location: str = None  # 事件发生地点
    cause: str = None  # 事件原因
    result: str = None  # 事件结果
    manner: str = None  # 事件方式
