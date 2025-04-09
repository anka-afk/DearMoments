from dear_moments.service import Services
from dear_moments.app_context import AppContext
from dear_moments.service import Services
import json


class MessageProcessor:
    """
    消息处理器, 接收到消息后, 先进行处理
    """

    def __init__(self):
        self.logger = AppContext.get_instance().get("logger")

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
        response = await Services.llm_service().get_response(prompt)
        # 检验返回的事件框架是否符合预期格式
        event_frame = await self.validate_event_frame(response)
        if not event_frame:
            self.logger.error("返回的事件框架格式不正确, 进行重试")
            # 进行重试
            response = await Services.llm_service().get_response(prompt)
            event_frame = await self.validate_event_frame(response)
            if not event_frame:
                self.logger.error("重试后返回的事件框架格式仍不正确")
                return None
        # 测试输出
        self.logger.info(f"提取的事件框架: {event_frame}")
        return event_frame

    async def validate_event_frame(self, response: str) -> dict:
        """验证LLM返回的事件框架是否符合预期格式

        Args:
            response (str): LLM返回的响应

        Returns:
            dict: 验证后的事件框架字典，如果验证失败则返回空字典
        """

        try:
            # 尝试解析JSON
            event_frame = json.loads(response)

            # 验证必要字段
            required_fields = [
                "type",
                "participants",
                "time",
                "location",
                "cause",
                "result",
                "manner",
            ]
            for field in required_fields:
                if field not in event_frame:
                    print(f"事件框架缺少必要字段: {field}")
                    return {}

            # 验证participants字段是否为字典类型
            if not isinstance(event_frame["participants"], dict):
                print("participants字段格式错误，应为字典类型")
                return {}

            return event_frame
        except json.JSONDecodeError:
            print(f"无法解析LLM返回的JSON格式 {response}")
            return {}
        except Exception as e:
            print(f"验证事件框架时发生错误: {str(e)}")
            return {}
