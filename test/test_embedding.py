import aiohttp
import asyncio
import json

API_KEY = input("API_KEY:")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-exp-03-07:embedContent?key={API_KEY}"


async def get_embedding(text):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "models/gemini-embedding-exp-03-07",
        "content": {"parts": [{"text": text}]},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return await response.text()


async def main():
    texts = ["今天天气不错", "今天是晴天", "今天没有下雨"]

    embeddings = await asyncio.gather(*[get_embedding(text) for text in texts])

    # 返回为一个列表, 其中每个元素是一个字典,
    # print(embeddings[0].keys())
    # 返回dict_keys(['embedding'])
    # print(type(embeddings[0]["embedding"]))
    # 也是一个字典
    # print(embeddings[0]["embedding"].keys())
    # 返回dict_keys(['values'])
    # print(type(embeddings[0]["embedding"]["values"]))
    # 返回<class 'list'>
    # print(embeddings[2])
    # print(type(embeddings[0]["embedding"]["values"][0]))
    # 返回<class 'float'>

    """
    要获取一个embedding, 路径为response->embedding->values, 是一个float列表
    """

    # for text, embedding in zip(texts, embeddings):
    #     print(f"Text: {text} \n Embedding: {embedding}\n")


asyncio.run(main())
