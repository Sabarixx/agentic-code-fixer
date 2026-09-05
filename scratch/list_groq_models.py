import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

headers = {"Authorization": f"Bearer {api_key}"}
resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
if resp.status_code == 200:
    models = [m["id"] for m in resp.json()["data"]]
    print("AVAILABLE MODELS:", models)
else:
    print("FAILED:", resp.status_code, resp.text)
