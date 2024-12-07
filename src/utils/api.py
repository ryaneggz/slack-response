import requests
from src.config import *

def query_endpoint(
    question, 
    thread_id=None, 
    channel_id=None, 
    images=None, 
    channel_system_messages=None, 
    channel_tools=None
):
    endpoint = f"{CHAT_ENDPOINT}/{thread_id}" if thread_id else CHAT_ENDPOINT
    payload = {
        "system": channel_system_messages.get(channel_id, SYSTEM_PROMPT),  # Get channel-specific system message or default
        "query": question,
        "stream": False,
        "tools": channel_tools.get(channel_id, []),  # Get tools for this channel
        "images": images or []  # Add images list to payload
    }

    response = requests.post(endpoint, json=payload, headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
    if response.status_code == 200:
        data = response.json()
        return data.get("thread_id"), data.get("answer", {}).get("content", "I could not find an answer.")
    else:
        return None, f"Error: {response.status_code}"