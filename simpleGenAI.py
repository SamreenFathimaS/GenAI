from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
llm = OpenAI(api_key=os.getenv("OPENAI_API_Key"),temperature=0.7)
prompt = PromptTemplate(
input_variables=["user_input"],
template = """
you are a helpful Ai assistant :
user says: {user_input}
your response:
"""
)

chain= LLMChain(llm=llm, prompt=prompt)

if __name__ == "__main__":
 user_input = input("Ask me anything: ")
response = chain.run({"user_input":user_input})  
print("AI Says:", response)