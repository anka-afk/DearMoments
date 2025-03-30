# 一个简单的聊天窗口实现

import os
import time
import threading
import json
import base64
import asyncio
from typing import List, Optional
from LLM_Chat import log_queue, SimpleGeminiClient, log_process


class LLMChat:
    def __init__(self, api_key: str, model_name: str, api_url: str, timeout: int = 120):
        """
        初始化LLMChat类

        Args:
            api_key (str): API密钥
            model_name (str): 模型名称
            api_url (str): API URL
            timeout (int): 超时时间(秒)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.conversation_history = []
        self.api_url = api_url
        self.timeout = timeout
        self.client = SimpleGeminiClient(api_key, api_url, timeout)

        log_queue.put(f"LLMChat initialized with model: {self.model_name}")

    def add_message(self, role: str, content: str):
        """添加消息到对话历史

        Args:
            role (str): 角色(user/assistant)
            content (str): 消息内容
        """
        self.conversation_history.append({"role": role, "content": content})

    async def list_models(self) -> List[str]:
        """列出可用的模型

        Returns:
            List[str]: 可用模型列表
        """
        return await self.client.models_list()

    async def encode_image_bs64(self, image_path: str) -> str:
        """将图片转换为base64编码

        Args:
            image_path (str): 图片路径

        Returns:
            str: base64编码的图片数据
        """
        try:
            with open(image_path, "rb") as f:
                image_bs64 = base64.b64encode(f.read()).decode("utf-8")
                return image_bs64
        except Exception as e:
            log_queue.put(f"图片编码失败: {str(e)}")
            return ""

    async def send_message(
        self, user_input: str, image_path: Optional[str] = None
    ) -> str:
        """发送消息到LLM

        Args:
            user_input (str): 用户输入
            image_path (Optional[str]): 图片路径

        Returns:
            str: LLM回复
        """
        try:
            log_queue.put(f"发送消息: {user_input}")

            # 准备Gemini格式的对话历史
            google_genai_conversation = []

            # 添加历史消息
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    google_genai_conversation.append(
                        {"role": "user", "parts": [{"text": msg["content"]}]}
                    )
                elif msg["role"] == "assistant":
                    google_genai_conversation.append(
                        {"role": "model", "parts": [{"text": msg["content"]}]}
                    )

            # 准备当前用户消息
            parts = [{"text": user_input}]

            # 如果有图片，添加图片
            if image_path:
                base64_image = await self.encode_image_bs64(image_path)
                if base64_image:
                    parts.append(
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image,
                            }
                        }
                    )
                    log_queue.put(f"添加了图片: {image_path}")

            google_genai_conversation.append({"role": "user", "parts": parts})

            # 记录这条消息到历史(只记录文本部分)
            self.add_message("user", user_input)

            # 发送请求
            start_time = time.time()
            response = await self.client.generate_content(
                contents=google_genai_conversation,
                model=self.model_name,
                temperature=0.7,
                max_tokens=1000,
            )
            end_time = time.time()
            log_queue.put(f"请求完成，耗时 {end_time - start_time:.2f} 秒")

            # 解析响应
            if "candidates" in response and len(response["candidates"]) > 0:
                # 提取文本部分
                reply_parts = response["candidates"][0]["content"]["parts"]
                reply_text = ""
                for part in reply_parts:
                    if "text" in part:
                        reply_text += part["text"]

                # 记录到历史
                self.add_message("assistant", reply_text)
                log_queue.put(f"收到回复: {reply_text[:100]}...")
                return reply_text
            else:
                error_msg = f"无效的响应格式: {json.dumps(response)[:100]}..."
                log_queue.put(error_msg)
                return f"错误: {error_msg}"
        except Exception as e:
            error_msg = f"发送消息时出错: {str(e)}"
            log_queue.put(error_msg)
            return f"错误: {error_msg}"

    async def close(self):
        """关闭客户端会话"""
        await self.client.close()


async def async_main():
    """异步主函数"""
    from .args_parser import args

    # 检查API密钥
    api_key = args.api_key or os.environ.get("API_KEY")
    if not api_key:
        print("错误: 请提供API密钥，可通过--api_key参数或API_KEY环境变量设置")
        return

    # 创建聊天实例
    chat = LLMChat(api_key, args.model, args.api_url, args.timeout)

    # 欢迎信息
    print("\n=== 命令行LLM聊天 ===")
    print(f"当前模型: {args.model}")
    print(f"API服务: {args.api_url}")
    print("输入 'exit' 或 'quit' 退出")
    print("输入 'clear' 清除对话历史")
    print("输入 'models' 查看可用模型列表")
    print("可以通过 --image 参数添加图片")
    print("开始聊天吧!\n")

    try:
        while True:
            user_input = input("\n> ")

            if user_input.lower() in ["exit", "quit"]:
                break

            if user_input.lower() == "clear":
                chat.conversation_history = []
                log_queue.put("已清除对话历史")
                continue

            if user_input.lower() == "models":
                print("\n正在获取可用模型列表...")
                models = await chat.list_models()
                if models:
                    print("可用模型列表:")
                    for model in models:
                        print(f"- {model}")
                else:
                    print("获取模型列表失败，请检查API密钥和网络连接")
                continue

            if not user_input.strip():
                continue

            # 发送消息并获取响应
            response = await chat.send_message(user_input, args.image)

            # 打印响应
            print(f"\n{response}\n")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
    finally:
        # 关闭客户端
        await chat.close()

        # 通知日志线程退出
        log_queue.put("EXIT")
        print("\n退出程序...")


def main():
    """主函数，启动日志线程和运行异步主循环"""
    # 启动日志线程
    log_thread = threading.Thread(target=log_process, daemon=True)
    log_thread.start()

    # 运行异步主循环
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
