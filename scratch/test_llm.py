import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

try:
    response = llm.invoke("Say hello in one sentence.")
    print("SUCCESS:", response.content)
except Exception as e:
    print("ERROR:", e)