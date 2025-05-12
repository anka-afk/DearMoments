from dear_moments.service import Services
from dear_moments.app_context import AppContext
from dear_moments.service import Services
from dear_moments.models import Message, SystemPrompt, ContextList, Context
from dear_moments.resources import StoragePrompts
import json


class MessageProcessor:
    """
    消息处理器, 接收到消息后, 先进行处理
    """

    def __init__(self):
        self.logger = AppContext.get_instance().get("logger")

    async def message_to_event_frame(self, message: Message):
        """利用LLm提取事件框架

        Args:
            message (Message): 消息对象
        """

        # ===================================================
        #                     Prompt构建
        # ===================================================
        system_prompt = SystemPrompt.get(message.memory_id)

        # 获取上下文
        context = ContextList.get_by_memory_id(message.memory_id)

        prompt = StoragePrompts.get_information_extract_prompt(
            system_prompt=system_prompt,
            examples="",
            conversations=context.to_str(),
            topic_examples="",
            tab=" ",
        )

        # ====================================================
        #               调用LLM进行事件框架提取
        # ====================================================
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

    async def save_to_context(self, message: Message):
        memory_id = message.memory_id
        # 获取上下文对象
        context = ContextList.get_by_memory_id(memory_id)
        if context is None:
            # 如果上下文不存在, 则创建一个新的上下文
            context = Context(memory_id=memory_id, context=[])
            ContextList.add(context)

        # 将消息添加到上下文中
        context.add(message)
