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

    for text, embedding in zip(texts, embeddings):
        print(f"Text: {text} \n Embedding: {embedding}\n")


asyncio.run(main())
