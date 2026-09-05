import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

for model_name in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "groq/compound-mini"]:
    try:
        llm = ChatGroq(model=model_name, api_key=os.getenv("GROQ_API_KEY"), timeout=10)
        res = llm.invoke("What is 2+2? Reply with only the number.")
        print(f"MODEL {model_name} OK:", res.content.strip())
        break
    except Exception as e:
        print(f"MODEL {model_name} FAILED:", e)
