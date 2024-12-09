import os

# App configuration
APP_USERNAME = os.getenv("APP_USERNAME", "admin")
APP_PASSWORD = os.getenv("APP_PASSWORD", "test1234")
BASE_API_URL = os.environ.get("BASE_API_URL", "https://graphchat.promptengineers.ai")
CHAT_ENDPOINT = f"{BASE_API_URL}/llm"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:test1234@localhost:5432/slack_agent?sslmode=disable")
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}
SYSTEM_PROMPT = ("You are a helpful Slack assistant. Be concise and to the point.")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
TOOLS_ENDPOINT = f"{BASE_API_URL}/tools"


