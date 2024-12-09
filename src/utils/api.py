import requests
from src.config import *

def query_endpoint(
    question: str, 
    thread_id: str = None,
    images: list = None, 
    channel_system_messages: str = None, 
    channel_tools: list = None
):
    endpoint = f"{CHAT_ENDPOINT}/{thread_id}" if thread_id else CHAT_ENDPOINT
    payload = {
        "system": channel_system_messages or SYSTEM_PROMPT,
        "query": question,
        "stream": False,
        "tools": channel_tools or [],
        "images": images or []
    }

    response = requests.post(endpoint, json=payload, headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
    if response.status_code == 200:
        data = response.json()
        return data.get("thread_id"), data.get("answer", {}).get("content", "I could not find an answer.")
    else:
        return None, f"Error: {response.status_code}"