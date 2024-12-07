import os

# Environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# App configuration
APP_USERNAME = os.getenv("APP_USERNAME", "admin")
APP_PASSWORD = os.getenv("APP_PASSWORD", "test1234")
BASE_API_URL = os.environ.get("BASE_API_URL", "https://graphchat.promptengineers.ai")
CHAT_ENDPOINT = f"{BASE_API_URL}/llm"
TOOLS_ENDPOINT = f"{BASE_API_URL}/tools"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}

# System prompt
SYSTEM_PROMPT = ("You are a helpful Slack assistant. Be concise and to the point.")