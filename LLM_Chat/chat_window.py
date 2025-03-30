# 一个简单的聊天窗口实现

import os
import sys
import time
import logging
import threading
import queue
import json
import base64
import argparse
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

import aiohttp
import requests

# 日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# 命令行参数
parser = argparse.ArgumentParser(description="Chat with LLM")
parser.add_argument("--api_key", type=str, help="API key for LLM")
parser.add_argument("--model", type=str, default="gemini-2.0-flash", help="Model name")
parser.add_argument(
    "--api_url",
    type=str,
    default="https://gemini-proxy.808711.xyz/",
    help="API URL",
)
parser.add_argument("--log_file", type=str, default="chat.log", help="Log file name")
parser.add_argument("--timeout", type=int, default=120, help="API timeout in seconds")
parser.add_argument("--image", type=str, help="Path to image file to include in chat")
args = parser.parse_args()

# 消息队列用于线程间通信
log_queue = queue.Queue()


class SimpleGeminiClient:
    """简单的Gemini API客户端"""

    def __init__(self, api_key: str, api_base: str, timeout: int = 120) -> None:
        """初始化Gemini API客户端

        Args:
            api_key (str): API密钥
            api_base (str): API基础URL
            timeout (int, optional): 超时时间(秒). 默认为 120秒.
        """
        self.api_key = api_key
        if api_base.endswith("/"):
            self.api_base = api_base[:-1]
        else:
            self.api_base = api_base

        if "/v1" in self.api_base or "/v1beta" in self.api_base:
            self.api_base = self.api_base.split("/v1")[0].split("/v1beta")[0]
            log_queue.put(
                f"警告: API URL包含版本路径，已自动移除。使用基础URL: {self.api_base}"
            )

        self.timeout = timeout
        # 使用aiohttp创建异步客户端会话
        self.client = None

        # 记录初始化信息
        log_queue.put(f"初始化Gemini客户端，基础URL: {self.api_base}")

    async def ensure_client(self):
        """确保客户端会话已创建"""
        if self.client is None:
            self.client = aiohttp.ClientSession(trust_env=True)

    async def close(self):
        """关闭客户端会话"""
        if self.client:
            await self.client.close()
            self.client = None

    async def models_list(self) -> List[str]:
        """获取可用模型列表

        Returns:
            List[str]: 可用模型列表
        """
        await self.ensure_client()
        request_url = f"{self.api_base}/v1beta/models?key={self.api_key}"

        log_queue.put(f"正在获取模型列表: {request_url}")

        try:
            async with self.client.get(request_url, timeout=self.timeout) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    log_queue.put(f"获取模型列表失败: {resp.status} - {error_text}")
                    return []

                response = await resp.json()

                models = []
                for model in response.get("models", []):
                    if "generateContent" in model.get("supportedGenerationMethods", []):
                        models.append(model["name"].replace("models/", ""))

                log_queue.put(f"获取到 {len(models)} 个可用模型")
                return models
        except Exception as e:
            log_queue.put(f"获取模型列表出错: {str(e)}")
            return []

    async def generate_content(
        self,
        contents: List[dict],
        model: str = "gemini-1.5-flash",
        system_instruction: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """生成内容

        Args:
            contents (List[dict]): 对话内容
            model (str, optional): 模型名称. 默认为 "gemini-2.0-flash".
            system_instruction (str, optional): 系统指令. 默认为 "".
            temperature (float, optional): 温度参数. 默认为 0.7.
            max_tokens (int, optional): 最大生成token数. 默认为 1000.

        Returns:
            dict: API响应
        """
        await self.ensure_client()

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        api_version = "v1beta"
        request_url = f"{self.api_base}/{api_version}/models/{model}:generateContent?key={self.api_key}"

        log_queue.put(f"正在发送请求到 {model}")
        log_queue.put(f"请求URL: {request_url.split('?')[0]}")

        try:
            async with self.client.post(
                request_url, json=payload, timeout=self.timeout
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    log_queue.put(f"API请求失败: {resp.status} - {error_text}")
                    raise Exception(f"API请求失败: {resp.status} - {error_text}")

                if "application/json" in resp.headers.get("Content-Type", ""):
                    response = await resp.json()
                    return response
                else:
                    text = await resp.text()
                    log_queue.put(f"API返回了非JSON数据: {text}")
                    raise Exception(f"API返回了非JSON数据: {text[:100]}...")
        except aiohttp.ClientError as e:
            log_queue.put(f"API请求出错: {str(e)}")
            raise Exception(f"API请求出错: {str(e)}")


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


def log_process():
    """日志处理线程，将日志写入文件并打印到日志窗口"""
    log_file = open(args.log_file, "a", encoding="utf-8")
    log_file.write(f"\n--- 新会话开始: {datetime.now()} ---\n")
    log_file.flush()

    print(f"日志进程已启动，日志将写入 {args.log_file}")

    try:
        while True:
            message = log_queue.get()
            if message == "EXIT":
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"

            # 写入日志文件
            log_file.write(log_entry)
            log_file.flush()

            # 输出到控制台
            print(log_entry, end="")

            log_queue.task_done()
    except KeyboardInterrupt:
        pass
    finally:
        log_file.close()
        print("日志进程已关闭")


async def async_main():
    """异步主函数"""
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
