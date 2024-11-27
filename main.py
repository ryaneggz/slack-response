import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initialize the app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Endpoint configuration
API_URL = "https://graphchat.promptengineers.ai/llm"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}

# Function to send a query to the API
def query_endpoint(question):
    payload = {
        "query": question,
        "stream": False,
        "system": "You are a helpful assistant.",
        "tools": [],
        "visualize": False,
    }
    response = requests.post(API_URL, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("answer", "I couldn't find an answer.").get("content", "I couldn't find an answer.")
    else:
        return f"Error: {response.status_code}"

# Listener for messages where the bot is tagged
@app.event("app_mention")
def handle_app_mention(event, say):
    channel_id = event['channel']
    user_id = event['user']
    text = event['text']
    # Extract the query, assuming it's the text after the mention
    question = text.split(maxsplit=1)[-1] if len(text.split()) > 1 else "What can I help you with?"
    print(f"Received question from USER <@{user_id}> in CHANNEL <#{channel_id}>: {question}")
    # Query the API
    response = query_endpoint(question)
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
