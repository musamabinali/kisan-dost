import asyncio
import os
from openai import AsyncOpenAI

os.environ["GROQ_API_KEY"] = "your_groq_key_here"

async def main():
    client = AsyncOpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    try:
        models = await client.models.list()
        print("COUNT", len(models.data))
        for m in models.data[:30]:
            print(m.id)
    except Exception as e:
        print("ERR", type(e).__name__, e)

asyncio.run(main())
