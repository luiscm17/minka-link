import asyncio
import os
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("GITHUB_ENDPOINT")
model = os.getenv("GITHUB_MODEL")
token = os.getenv("GITHUB_TOKEN")

async def main():
    async with (
        ChatAgent(
            chat_client=OpenAIChatClient(api_key=token, base_url=endpoint, model_id=model),
            instructions="You are good at telling jokes.",
            model=model
        ) as agent,
    ):
        result = await agent.run("Tell me a joke about a pirate.")
        print(result.text)

if __name__ == "__main__":
    asyncio.run(main())