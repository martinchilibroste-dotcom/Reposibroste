import os
import requests
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

url = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}
payload = {"q": "OpenAI últimas noticias", "num": 3, "hl": "es"}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    for i, item in enumerate(data.get("organic", []), 1):
        print(f"{i}. {item['title']}")
        print(f"   {item['link']}\n")
else:
    print(f"Error {response.status_code}: {response.text}")
