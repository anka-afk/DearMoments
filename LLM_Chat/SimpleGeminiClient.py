from .log import log_queue
import aiohttp
from typing import List


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
