import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

# Initialize the app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Endpoint configuration
BASE_API_URL = os.environ.get("BASE_API_URL", "https://graphchat.promptengineers.ai")
CHAT_ENDPOINT = f"{BASE_API_URL}/llm"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}

# In-memory storage for thread IDs
conversation_threads = {}

# Function to send a query to the API
def query_endpoint(question, thread_id=None):
    endpoint = f"{CHAT_ENDPOINT}/{thread_id}" if thread_id else CHAT_ENDPOINT
    payload = {
        "query": question,
        "stream": False,
        "tools": [],
    }
    response = requests.post(endpoint, json=payload, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get("thread_id"), data.get("answer", {}).get("content", "I couldn't find an answer.")
    else:
        return None, f"Error: {response.status_code}"

# Listener for messages where the bot is tagged
@app.event("app_mention")
def handle_app_mention(event, say):
    channel_id = event["channel"]
    user_id = event["user"]
    text = event["text"]

    # Extract the query, assuming it's the text after the mention
    question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"

    # Check if there's an existing thread for this channel
    thread_id = conversation_threads.get(channel_id)

    print(f"Received question from USER <@{user_id}> in CHANNEL <#{channel_id}>: {question} (Thread ID: {thread_id})")

    # Query the API
    new_thread_id, response = query_endpoint(question, thread_id)

    # Update thread context
    if new_thread_id:
        conversation_threads[channel_id] = new_thread_id

    say(response)

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>! How can I help you today?")

# Start the app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
