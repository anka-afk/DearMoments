from dear_moments.service import Services


class MessageProcessor:
    """
    消息处理器, 接收到消息后, 先进行处理
    """

    services: Services

    def __init__(self, services: Services):
        self.services = services

    async def message_to_event_frame(self, event_text: str):
        """利用LLm提取事件框架

        Args:
            event_text (str): 事件文本
        """
        prompt = f"""
        请从以下文本中提取事件信息，并以JSON格式返回：
        {event_text}

        提取为以下格式:
        {{
        "type": "事件类型",
        "participants": {{"role1": "entity1", "role2": "entity2"}},
        "time": "时间信息",
        "location": "地点信息",
        "cause": "事件原因",
        "result": "事件结果",
        "manner": "事件方式"
        }}
        """

        # 调用LLM进行事件框架提取
        llm_service = self.services.llm_service
        response = await Services.llm_service.get_response(prompt)
