from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
import asyncio
load_dotenv()

async def main():
 api_key = os.getenv('OPENAI_API_KEY')
 model_client = OpenAIChatCompletionClient(model='gpt-4.1', api_key=api_key)
 assistant = AssistantAgent(name ="Chand", model_client=model_client)
 result = await assistant.run(task = "tell me a life quotes in tamil")
 print(result.messages[-1].content)
asyncio.run(main())